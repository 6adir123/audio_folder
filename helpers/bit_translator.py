"""
we will use a varicode dictionary for our translation process
https://en.wikipedia.org/wiki/Varicode

note that due to microphone/ speaker array of my computer which is usually subpar from standart (my computer's speakers make hissing noises in high frequencies)
I can't tell you the volume level needed in order to have results is below 50%



the protocol consists of password+space. the listener knows that space is a seperator of passwords


please make sure there are two types of frames, frames got from the PyAudio which we process (which are chunks of data)
and frames used for our protocl to build bits







"""

varicode_dict = {
    " ": "1",
    "!": "111111111",
    '"': "101011111",
    '#': "111110101",
    '$': "111011011",
    '%': "1011010101",
    '&': "1010111011",
    "'": "101111111",
    '(': "11111011",
    ')': "11110111",
    '*': "101101111",
    '+': "111011111",
    ',': "1110101",
    '-': "110101",
    '.': "1010111",
    '/': "110101111",
    '0': "10110111",
    '1': "10111101",
    '2': "11101101",
    '3': "11111111",
    '4': "101110111",
    '5': "101011011",
    '6': "101101011",
    '7': "110101101",
    '8': "110101011",
    '9': "110110111",
    ':': "11110101",
    ';': "110111101",
    '<': "111101101",
    '=': "1010101",
    '>': "111010111",
    '?': "1010101111",
    '@': "1010111101",
    'A': "1111101",
    'B': "11101011",
    'C': "10101101",
    'D': "10110101",
    'E': "1110111",
    'F': "11011011",
    'G': "11111101",
    'H': "101010101",
    'I': "1111111",
    'J': "111111101",
    'K': "101111101",
    'L': "11010111",
    'M': "10111011",
    'N': "11011101",
    'O': "10101011",
    'P': "11010101",
    'Q': "111011101",
    'R': "10101111",
    'S': "1101111",
    'T': "1101101",
    'U': "101010111",
    'V': "110110101",
    'W': "101011101",
    'X': "101110101",
    'Y': "101111011",
    'Z': "1010101101",
    '[': "111110111",
    '\\': "111101111",
    ']': "111111011",
    '^': "1010111111",
    '_': "101101101",
    '`': "1011011111",
    'a': "1011",
    'b': "1011111",
    'c': "101111",
    'd': "101101",
    'e': "11",
    'f': "111101",
    'g': "1011011",
    'h': "101011",
    'i': "1101",
    'j': "111101011",
    'k': "10111111",
    'l': "11011",
    'm': "111011",
    'n': "1111",
    'o': "111",
    'p': "111111",
    'q': "110111111",
    'r': "10101",
    's': "10111",
    't': "101",
    'u': "110111",
    'v': "1111011",
    'w': "1101011",
    'x': "11011111",
    'y': "1011101",
    'z': "111010101",
    '{': "1010110111",
    '|': "110111011",
    '}': "1010110101",
    '~': "1011010111",
}

decode_varicode_dict = {}
for k, v in varicode_dict.items():
    decode_varicode_dict[v] = k


def encode(string):
    """
    encode:
        input: gets a string
        output: encodes it according to dictionary,checks also for using wrong text, then sends an ''
    """
    try:
        if string == '':
            return ''
        result = []
        for c in string:
            result.append(varicode_dict[c])
        return '00'.join(result) + '00'
    except:
        return ''


def decode(string):
    """
    decode:
        input: gets a character
        output: if able to decode, decodes it, otherwise empty string
    """
    try:
        return decode_varicode_dict[''.join([str(i) for i in string])]
    except:  # in case of disturbance, decoding won't be done right, and won't be calculated in our word count
        return ''
