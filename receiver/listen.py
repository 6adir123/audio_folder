import queue
import threading
import time
import pyaudio
import sys
from helpers import encryptor, audio_utils, bit_translator, options
from receiver import timer, folder_setup
import os
import logging
import sqlite3


class Listen:

    def __init__(self, frequency, hash_password, folder):
        logging.basicConfig(filename='listen.log', filemode='a', format='%(asctime)s - %(message)s',
                            datefmt='%d-%b-%y %H:%M:%S')
        logging.warning('(RUN)')
        self.FORMAT = pyaudio.paInt16
        self.points_frame_length = options.points_frame_length  # frame of points, not frames of data (don't confuse them)
        self.chunk = options.chunk  # chunk data
        self.search_freq = frequency  # the searched frequency
        self.rate = options.rate  # the sample rate
        self.char_delim = [int(x) for x in options.char_delim]  # the  character delimiter   
        self.word_delim = ' '  # the word delimiter
        self.frames_per_buffer = self.chunk * 10  # the amount of frames per buffer (for pyaudio)
        self.stream = None  # the audio stream of pyaudio
        # raw audio frames
        self.in_frames = queue.Queue(options.in_length)
        # fft points
        self.points = queue.Queue(
            options.in_length)  # queue of points, which are amplitude values of fft in the searched frequency
        self.bits = queue.Queue(options.in_length / self.points_frame_length)  # bits of information
        self.words = queue.Queue(options.in_length)  # words that might be passwords
        self.timeout = options.timeout  # timeout values in case one of the queues is Empty
        self.threshold = 9000  # the buttom threshold for points, if average of 3 points higher, bit is 1, otherwise bit is 0
        self.PASSWORD = ''  # password placeholder
        self.t = timer.Timer()  # timer for password wrong issues
        self.freq_t = timer.Timer()  # the timeout for frequency wrong issues
        self.password_hash = hash_password  # the hash of our password in sha256
        self.folder = folder  # folder path
        self.interval = options.time_interval  # time interval for wrong password
        self.freq_time_interval = options.freq_time_interval  # time interval of no frequency detected

    def run(self):
        """
        :return: start running the program, by starting its processing threads stream processing
        """
        # our threads to the different processing functions
        functions = [self.process_frames, self.process_points, self.process_bits, self.process_password]
        print('\033[1mwelcome to audio folder receiver')
        print('listening...\033[0m')
        for func in functions:
            thread = threading.Thread(target=func)
            thread.daemon = True
            thread.start()
        self.t.reset()  # start the wrong password timer
        self.freq_t.reset()  # start the wrong frequency timer
        self.start_analyzing_stream()

    def time_stop(self):
        """

        :return: locks the folder in case of quit from program
        """
        try:
            time.sleep(self.timeout)
        except:
            encryptor.lock_folder(self.PASSWORD, self.folder)
            print('code quited, folder was encrypted', file=sys.stderr)
            self.stream.close()
            sys.exit(1)

    def process_frames(self):
        """

        :return:listens to frames and adds the value of fft in the frequency we care about = turns them into points,also lock the folder if near perfect frequency isn't detected
        """
        start_receiving = True
        while True:
            try:
                frame = self.in_frames.get(False)
                fft_sample, window_length = audio_utils.fft(frame)
                freq = audio_utils.get_freq(fft_sample, window_length, self.rate)
                point = audio_utils.get_point(fft_sample, self.search_freq, self.rate, self.chunk)
                self.points.put(point)
                # stops reading in case frequency is below searched frequency for 3 seconds
                if abs(self.search_freq - freq) < 1:
                    start_receiving = False
                    self.freq_t.reset()
                elif self.freq_t.check_difference() > self.freq_time_interval or start_receiving:
                    # empty all queues after 3 seconds of wrong frequency and lock the folder
                    audio_utils.clear_queue(self.points, self.bits, self.words)
                    encryptor.lock_folder(self.PASSWORD, self.folder)
                    self.PASSWORD = ''

            except queue.Empty:
                self.time_stop()

    def process_points(self):
        """

        :return: processes the points from the list of frames, turns the points into bits while the program runs
        """

        # always running!!!
        while True:
            current_points = []
            while len(current_points) < self.points_frame_length:
                try:
                    current_points.append(self.points.get(False))
                except queue.Empty:
                    self.time_stop()
            # checking if there's a signal
            while audio_utils.get_bit(current_points,
                                      self.points_frame_length) < self.threshold:  # in case the frequency timer doesn't elapse until we get here, points will be stopped from getting to their destination here
                try:
                    current_points.append(self.points.get(False))
                    current_points = current_points[1:]
                except queue.Empty:
                    self.time_stop()

            self.bits.put(0)
            self.bits.put(0)

            # converts the points into bit pattern of one character
            check_bits = []
            while True:
                if len(current_points) == self.points_frame_length:
                    bit = int(audio_utils.get_bit(current_points,
                                                  self.points_frame_length) > self.threshold)  # check if the points frame is under threshold or not, to decide the sign of the bit
                    current_points = []
                    self.bits.put(bit)
                    check_bits.append(bit)
                # if we've only seen low bits for a while assume the next message might not be on the same bit boundary and were moving a bit boundry, meaning we need to check again the checks above
                if len(check_bits) > self.points_frame_length:
                    if sum(check_bits) == 0:
                        break
                    check_bits = check_bits[1:]
                try:
                    current_points.append(self.points.get(False))
                except queue.Empty:
                    self.time_stop()

    def process_bits(self):
        """

        :return: processes the bits and creates words out of them
        """
        word = ''
        while True:
            current_bits = []
            # while the last two characters are not the char_delim
            while len(current_bits) < len(self.char_delim) or current_bits[-len(self.char_delim):len(
                    current_bits)] != self.char_delim:  # check and splits letters by delimiter
                if len(current_bits) > 12:
                    print('please make sure to adjust volume / phone position', file=sys.stderr)
                    current_bits = []
                try:
                    current_bits.append(self.bits.get(False))
                except queue.Empty:
                    self.time_stop()
            ch = bit_translator.decode(current_bits[:-len(self.char_delim)])
            if ch == self.word_delim:
                self.words.put(word)
                word = ''

            else:
                word += ch

    def process_password(self):
        """

        :return:  processes the password and unlocks the file if the password is correct, else, if not hearing password or password is wrong for one and a half minute, locks the file, also adds wrong password
        to the log file
        """
        while True:
            try:
                word = encryptor.vigenere(self.words.get(False), cmd='d')  # decrypts the password
                if encryptor.generate_pbkdf2(word) == self.password_hash:  # check if it matches the hash
                    print('correct password')
                    logging.warning('%s,%d,right' % (self.folder, self.search_freq))
                    self.PASSWORD = word
                    encrypted_folder_name = encryptor.insert_enc_tag(self.folder) + '.zip'
                    if os.path.isfile(encrypted_folder_name):
                        encryptor.decrypt(word, encrypted_folder_name)
                        encryptor.unzip_file(self.folder + '.zip')

                    self.t.reset()
                else:
                    logging.warning('%s,%d,wrong' % (self.folder, self.search_freq))

            except:
                self.time_stop()
            if self.t.check_difference() > self.interval:
                encryptor.lock_folder(self.PASSWORD, self.folder)
                self.PASSWORD = ''

    def callback(self, in_data, frame_count, time_info,
                 status):  # I know we need only the in_data, but callback requires us to receive 4 arguments
        """

        :param in_data: data
        :param frame_count: frame count
        :param time_info: time info
        :param status: status of listening
        :return: splits the data into frames and puts them in the queue, returns a sign for the stream to continue
        """
        frames = list(audio_utils.chunks(audio_utils.unpack(in_data), self.chunk))
        for frame in frames:
            if not self.in_frames.full():
                self.in_frames.put(frame, False)
        return in_data, pyaudio.paContinue

    def start_analyzing_stream(self):
        """

        :return: start analyzing the information send by sound waves
        """

        p = pyaudio.PyAudio()
        self.stream = p.open(format=self.FORMAT, channels=options.channels, rate=options.rate,
                             input=True, frames_per_buffer=self.frames_per_buffer, stream_callback=self.callback)
        self.stream.start_stream()
        while self.stream.is_active():
            self.time_stop()


def get_from_sql(path):
    """

    :param path: the folder path
    :return: the frequency and password values of the path stored in the database
    """
    while True:
        try:
            conn = sqlite3.connect('folders.db')
            cursor = conn.execute('''
                    SELECT PATH,PASSWORD_HASH,FREQUENCY FROM FOLDER_DATA WHERE PATH=(?)
                    ''', (path,))
            res = cursor.fetchone()
            conn.close()
            return res[1], res[2]
        except:
            print('''the folder path doesn\'t appear in the database (maybe is was moved 
                  from its original location), redirecting you to folder databse setup''', file=sys.stderr)
            folder_setup.sql_setup(path)


def main(folder_path=None):
    """

    :return: listen for folder without setting it up
    """
    folder_setup.delete_from_sql()
    while True:

        if folder_path is None:
            folder_path = os.path.abspath(input('enter folder name: '))
            if not os.path.isfile(encryptor.insert_enc_tag(folder_path) + '.zip'):
                if os.path.isdir(folder_path) and folder_path != os.getcwd():
                    print('Folder isn\'t setup-ed, redirecting to folder setup', file=sys.stderr)
                    folder_setup.sql_setup(folder_path)
                else:
                    print('folder doesn\'t exist, please restart the program', file=sys.stderr)
                    sys.exit(1)

        password, freq = get_from_sql(folder_path)
        listener = Listen(int(freq), password, folder_path)
        break
    listener.run()


if __name__ == '__main__':
    main()
