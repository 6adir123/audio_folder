from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random
import os
import shutil
import zipfile
from helpers.options import keyword, salt
import sys
import logging
universe = [c for c in (chr(i) for i in range(32, 127))]
universe_len = len(universe)


def encrypt(password, filename):
    """
    Encrypt the file
    :param password: a password
    :param filename: The filename
    :return: N/A
    """
    print('encrypting')
    chunk_size = 64 * 1024
    output_file = insert_enc_tag(filename)
    # insert file size, Initialization vector for AES encryption, and salt for PBKDF2
    file_size = str(os.path.getsize(filename)).zfill(16)
    iv = Random.new().read(16)
    key = get_key(password)
    encryptor = AES.new(key, AES.MODE_CBC, iv)

    # encrypt the data
    with open(filename, 'rb') as in_file:
        with open(output_file, 'wb') as out_file:
            out_file.write(file_size.encode('utf-8'))
            out_file.write(iv)

            while True:
                chunk = in_file.read(chunk_size)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - (len(chunk) % 16))

                out_file.write(encryptor.encrypt(chunk))
    os.remove(filename)


def decrypt(password, filename):
    """
    decrypts the file
    :param password: a password
    :param filename: the filename
    :return: N/A
    """
    print('decrypting')
    chunk_size = 64 * 1024
    output_file = remove_enc_tag(filename)

    with open(filename, 'rb') as in_file:
        # gets file size, Initialization vector for AES encryption, and salt for PBKDF2
        file_size = int(in_file.read(16))
        iv = in_file.read(16)
        key = get_key(password)

        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(output_file, 'wb') as out_file:
            while True:
                chunk = in_file.read(chunk_size)

                if len(chunk) == 0:
                    break

                out_file.write(decryptor.decrypt(chunk))
            out_file.truncate(file_size)
    os.remove(filename)


def get_key(password):
    """
    turns a password into a key
    :param password: a password
    :return: the key for the decryption/encryption in sha256
    """

    return SHA256.new(password.encode()).digest()


def generate_pbkdf2(password):
    """
    generates an pbkdf2 of the key
    :param password: a string to hash
    :return: the pbkdf2 key
    """
    return PBKDF2(password, bytes.fromhex(salt)).hex()


def zip_file(path):
    """

    :param path: gets the path
    :return: zips it
    """
    zipf = zipfile.ZipFile(path + '.zip', 'w', zipfile.ZIP_DEFLATED)
    # zipf is zipfile handle
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                zipf.write(os.path.join(root, file))
            for dir in dirs:
                zipf.write(os.path.join(root, dir))
    except:
        print('No such folder', file=sys.stderr)
    if os.path.isdir(path):
        # wiping all the data in the folder
        os.system('rm -Prf %s' % path)
    zipf.close()


def unzip_file(file_path):
    """

    :param file_path: the file path
    :return: unzips it
    """
    try:
        zipf = zipfile.ZipFile(file_path)
        dir_path = file_path[:-4]
        os.mkdir(dir_path)
        zipf.extractall(dir_path)
        os.remove(file_path)

        if len(os.listdir(dir_path)) != 0:
            delete_extra = dir_path + dir_path
            move_to = '/'.join(dir_path.split('/')[:-1])
            os.system(': $(rsync -a %s %s)' % (delete_extra, move_to))
            shutil.rmtree(dir_path + '/' + dir_path.split('/')[1])

    except Exception as e:
        print(e, file=sys.stderr)


def vigenere(txt='', key=keyword, cmd='d'):
    """

    :param txt: the text
    :param key: the key
    :param cmd: encrypt/decrypt
    :return: the encrypted by vigenere text
    """
    if not txt:
        return
    if not key:
        print('Needs key.')
        return
    if cmd not in ('d', 'e'):
        print('Type must be "d" or "e".')
        return
    if any(t not in universe for t in key):
        print('Invalid characters in the key. Must only use ASCII symbols.')
        return

    ret_txt = ''
    k_len = len(key)

    for i, l in enumerate(txt):
        if l not in universe:
            ret_txt += l
        else:
            txt_idx = universe.index(l)

            k = key[i % k_len]
            key_idx = universe.index(k)
            if cmd == 'd':
                key_idx *= -1

            code = universe[(txt_idx + key_idx) % universe_len]

            ret_txt += code

    return ret_txt


def lock_folder(password, folder):
    """
    :password: the password to use in the encryption
    :folder: the folder name
    :return: locks the folder
    """
    logging.basicConfig(filename='listen.log', filemode='a', format='%(asctime)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')
    if password != '':
        if os.path.isdir(folder):
            logging.warning('%s,folder locked' % folder)
            zip_file(folder)
            encrypt(password, folder + '.zip')


def insert_enc_tag(path):
    """

    :param path: a path to a folder
    :return: inserts the (enc) before the folder name
    """
    params = path.split('/')
    return '/'.join(params[:-1]) + '/(enc)' + params[-1]


def remove_enc_tag(path):
    """

    :param path: the folder path
    :return: removes the (enc) before the folder name
    """
    params = path.split('/')
    return '/'.join(params[:-1]) + '/' + params[-1][5:]
