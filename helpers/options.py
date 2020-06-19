rate = 44100
freq = 20000 # default for telegram bot
channels = 1  # mono audio
points_frame_length = 3  # the length of the points frame (
chunk = 256  # length of data per point
datasize = chunk * points_frame_length
char_delim = "00"  # the seperator for varicode
word_delim = ' '  # the delimiter for words
keyword = 'the}quic(kbrown!\'fox{ju]mps!@#$%^&*_-+=.\'\><?|~`:;//over[thelazy)dog5829013746' + 'thequickbrownfoxjumpsoverthelazydog'.upper()  # a keyword for the vigenere encoding and decoding
timeout = 0.1  # timeout in case quues are empty
sample_width = 2
in_length = 4000  # length of queues
time_interval = 30  # time interval fro wrong password issues
freq_time_interval = 3  # time interval for wrong frequency issues
salt = '2354ddcaf31a25a1e19f1b622a52110d'
