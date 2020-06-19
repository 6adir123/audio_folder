from helpers import audio_utils, bit_translator, options
import wave
from helpers.encryptor import vigenere

CHANNELS = options.channels
RATE = options.rate
FREQ = options.freq
NO_FREQ = 0
DATASIZE = options.datasize
SAMPLE_WIDTH = options.sample_width


def make_buffer_from_bit_pattern(pattern, given_freq):
    """

    :param pattern: a bit pattern
    :param given_freq: high frequency value representing 1
    :return: make a psk31 wave from the bit pattern given (includes dealing with key clicks using cosine filter, and packing for wav file/ pyaudio stream)
    """
    # the tone's middle value is the bit's value and the left and right bits are the bits before and after
    # the buffer is then smoothed with a cosine filter

    last_bit = pattern[-1]
    output_buffer = []
    offset = 0

    for i in range(len(pattern)):
        bit = pattern[i]
        if i < len(pattern) - 1:
            next_bit = pattern[i + 1]
        else:
            next_bit = pattern[0]

        freq = given_freq if bit == '1' else NO_FREQ
        tone = audio_utils.produce_tone(freq, DATASIZE, offset=offset)
        output_buffer += audio_utils.smooth_transition(tone, before=last_bit == '0',
                                                       after=next_bit == '0')  # smoothing the tone (if needed and there's a jump between 1 and 0)
        offset += DATASIZE  # offset to the next tone
        last_bit = bit
    return audio_utils.pack_buffer(output_buffer)  # packing the buffer in order for stream to play it


def write_to_wav_file(msg, iden, given_freq=FREQ):
    """

    :param msg: the message from the telegram bot to make a sound of (the password)
    :param given_freq: the desired high frequency given
    :param iden: the chat id
    :return: writes the buffer repeatedly to a .wav file
    """
    pattern = bit_translator.encode(vigenere(msg, cmd='e') + options.word_delim)
    buffer = make_buffer_from_bit_pattern(pattern, given_freq)  # the buffer to write to the file
    wf = wave.open('%d_%d_output.wav' % (iden, given_freq), 'wb')
    wf.setnchannels(options.channels)
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(RATE)
    for i in range(25):
        wf.writeframes(b''.join(buffer))
    wf.close()
