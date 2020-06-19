import telebot
from maker import send
from helpers import bit_translator
import os

API_TOKEN = input('enter API token: ')

bot = telebot.TeleBot(API_TOKEN)


def char_counter(st, ch):
    """

    :param st: a string
    :param ch: a character
    :return: returns the amount of times the character is in the string
    """
    count = 0
    for s in st:
        if s == ch:
            count += 1
    return count


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    """

    :param message: a message
    :return: introduction
    """
    bot.reply_to(message, """\
Hi there, I am TelesonicBot.
I'm here to make the audio files for the decryption of your folder, please send me your password\r\n
if you want to send the password in a different frequency, please send in this format : freq(integer) password
\r\n example: 12500 hello\
""")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    """

    :param message: a message
    :return: a sound sample containing the password to the telegram user,and sends the password back to the user as well
    """
    iden = message.chat.id  # the chat id of the user
    print(iden)
    try:
        if bit_translator.encode(message.text) == '':
            raise Exception('password text isn\'t supported, please try again')
        if char_counter(message.text, ' ') == 0:
            formatted_msg = str(iden) + ':' + message.text
            send.write_to_wav_file(formatted_msg, iden)
            doc = open('%d_20000_output.wav' % iden, 'rb')
            os.remove('%d_20000_output.wav' % iden)
            bot.reply_to(message, formatted_msg)
            bot.send_audio(iden, doc, timeout=60)
        elif char_counter(message.text, ' ') == 1:
            st_list = message.text.split(' ')
            formatted_msg = str(iden) + ':' + st_list[1]
            if not st_list[0].isdigit() or int(st_list[0]) < 10000 or int(st_list[0]) > 20000 or int(
                    st_list[0]) % 10 != 0:
                raise Exception(
                    'frequency must be a positive number divisible by 10 and between 10000 and 20000,please try again')

            send.write_to_wav_file(formatted_msg, iden, int(st_list[0]))
            doc = open('%d_%s_output.wav' % (iden, st_list[0]), 'rb')
            os.remove('%d_%s_output.wav' % (iden, st_list[0]))
            bot.reply_to(message, formatted_msg)
            bot.send_audio(iden, doc, timeout=60)
        else:
            raise Exception('unsupported format, please try again')
    except Exception as e:
        bot.reply_to(message, e)


bot.polling(none_stop=True)
