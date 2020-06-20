import numpy as np
import struct
import math


def chunks(buffer, size):
    """
    :param buffer: a buffer
    :param size: the size to split into
    :return: splits the data into chunks
    """
    for i in range(0, len(buffer), size):
        yield buffer[i:i + size]


def unpack(buffer):
    """
    :param buffer: a buffer
    :return: unpacks the buffer as whole (while unpacking it by splitting into 2 chunks of data)
    """
    return unpack_buffer(list(chunks(buffer, 2)))


def unpack_buffer(buffer):
    """
    :param buffer: a buffer
    :return: returns an unpacked buffer
    """
    return [struct.unpack('h', frame)[0] for frame in buffer]


def pack_buffer(buffer):
    """
    :param buffer: gets a buffer
    :return: returns the buffer packed
    """
    return [struct.pack('h', frame) for frame in buffer]


def fft(signal):
    """
    :param signal: a signal
    :return: performs fft on the signal
    """

    windowed = signal * np.blackman(len(signal))  # getting the window of our signal
    fft_sample = np.fft.rfft(windowed)  # performing an discrete fourier transform on it (ony real numbers)
    return abs(fft_sample), len(windowed)


def get_peak(hertz, rate, chunk):
    """
    :param hertz: frequency
    :param rate: rate of sound
    :param chunk: size
    :return: returns the index of the requested frequency
    """
    return int(round((float(hertz) / rate) * chunk))


def get_freq(fft_sample, window_length, rate):
    """
    :param fft_sample: the fft sample received
    :param window_length: the length of the windowed signal
    :param rate: the rate of sound
    :return: the accurate frequency of our signal using the quadric interpulation method
    based on https://ccrma.stanford.edu/~jos/sasp/Quadratic_Interpolation_Spectral_Peaks.html
    """
    max_freq = np.argmax(abs(fft_sample))  # max fft frequency (not accurate)
    true_max_freq = parabolic(np.log(abs(fft_sample)),
                              max_freq)  # using the quadratic interpolation in order to get the most accurate frequency index
    return rate * true_max_freq / window_length  # the frequency itself


def get_point(fft_sample, freq_in_hertz, rate, chunk):
    """
    :param fft_sample: fft sample
    :param freq_in_hertz: frequency in hertz
    :param rate: the sample rate
    :param chunk: size of chunk
    :return: the fft value (amplitude) at the peak value of the searched frequency
    """
    peak_index = get_peak(freq_in_hertz, rate,
                          chunk)  # will be incorrect and low if the frequency is not right, returns a lower peak
    return fft_sample[peak_index]


def get_bit(points, frame_len):
    """
    :param points: points list
    :param frame_len: size of a frame of points
    :return: the bit represented by the points
    """

    return int(round(sum(points) / float(frame_len)))


def produce_tone(freq=400, size=4096, rate=44100, amp=12000.0, offset=0):
    """
    :param freq: frequency
    :param size: data size
    :param rate: rate
    :param amp: amplitude
    :param offset: offset of tone
    :return: combines them into a list of sine values, used for the psk31 waves making
    """
    sin_list = []
    for x in range(size):
        samp = math.sin(2 * math.pi * freq * ((x + offset) / float(rate)))
        sin_list.append(int(samp * amp))
    return sin_list


def smooth_transition(in_tone, before=True, after=True):
    """
    :param in_tone: data of tone
    :param before: information about the previous bit
    :param after: information about the following bit
    :return: cosine filter for psk31 waves, reduces key clicking
    """
    half = float(len(in_tone)) / 2
    freq = math.pi / (len(in_tone) / 2)  # the frequency of the filter
    out_tone = []

    for x in range(len(in_tone)):
        sample = in_tone[x]
        if (x < half and before) or (after and x >= half):
            sample = sample * (1 - math.cos(freq * x)) / 2  # smooths the wave in case of change in frequency
        out_tone.append(int(sample))

    return out_tone


def clear_queue(*args):
    """
    :param args: a list of queues
    :return: empty all of the queues
    for q in args:
    """
    for q in args:
        while not q.empty():
            q.get(False)


def parabolic(f, x):
    """
    quadratic interpolation: used to get the accurate frequency in get_freq
    :param f: a vector
    :param x: an index of a vector
    :return: x_coordinate: the x coordinate of the vertex of the parabola that goes through point x and its two neighbors
    """
    try:
        x_coordinate = 1 / 2 * (f[x - 1] - f[x + 1]) / (f[x - 1] - 2 * f[x] + f[x + 1]) + x
        return x_coordinate
    # there may be a runtime error at the beginning of the program, due o division by zero, this will fix the problem
    except RuntimeError:
        return 0
