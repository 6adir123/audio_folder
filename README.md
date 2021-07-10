# audio folder

## Introduction
The purpose of the code is **encrypting folders (in macOS) using passwords transmitted by sound**

## How to setup the folder and its password?
First of all, install python 3.7 and the modules in [requirements.txt](requirements.txt), then:
1) create a telegram bot token using bot father. [Instructions](https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token)
2) go to [telegram_bot.py](audio_folder/maker/telegram_bot.py), insert your API token, create your sound password, find your (id+:+password) to put in folder setup
3) go to [listen.py](audio_folder/receiver/listen.py) to lock the folder (insert the text displayed in telegram in the password field) and desired frequency

## How to run?
1) start [listen.py](audio_folder/receiver/listen.py) and write your folder path.
2) start the audio sample in your telegram bot next to your computer
3) enjoy :)

## requirements
* MacOS Catalina
* python 3.7
* numpy==1.18.4
* PyAudio==0.2.11
* pycrypto==2.6.1
* pyTelegramBotAPI==3.7.1
