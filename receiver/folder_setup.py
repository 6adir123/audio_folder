from helpers import encryptor, bit_translator
import os
from getpass import getpass
import sys
import sqlite3


def insert_into_sql(path, freq, password_hash):
    """

    :param path: folder path
    :param freq: the desired frequency
    :param password_hash: the password hash
    :return: inserts the information into the database
    """
    conn = sqlite3.connect('folders.db')
    cursor = conn.execute('''
    SELECT * FROM FOLDER_DATA WHERE PATH=(?)
    ''', (path,))
    if cursor.fetchone() is None:
        conn.execute('''
        INSERT INTO FOLDER_DATA (PATH,PASSWORD_HASH,FREQUENCY) VALUES (?,?,?)
        ''', (path, password_hash, int(freq)))
    else:
        conn.execute('''
        UPDATE FOLDER_DATA SET PASSWORD_HASH=(?),FREQUENCY=(?) WHERE PATH=(?)
        ''', (password_hash, int(freq), path))
    conn.commit()
    conn.close()


def ask_removal_of_folder():
    print("the folder already exists: do you want to override it?")
    response = ''
    while response.lower() not in {"yes", "no"}:
        response = input("Please enter yes or no: ")
    return response.lower() == "yes"


def sql_setup(folder_path):
    """

    :param folder_path: the folder path
    :return: inserts the password and frequency to the folder database, and encrypts the data with the password
    """
    while True:
        try:
            password = getpass('enter password: ')
            if  len(password) <= 10 or bit_translator.encode(password) == '' or password.find(' ') >= 0 or not password[0:9].isdigit() or \
                    password[9] != ':':
                raise Exception(
                    '''password must be varicode compatible, shouldn\'t include spaces, 
                    shouldn\'t be empty, should start with an chat id and include \':\' on the 10th digit''')
            freq = input('enter frequency: ')
            if not freq.isdigit() or int(freq) < 10000 or int(freq) > 20000 or int(
                    freq) % 10 != 0:  # due to limitations, frequencies must be in 500 jumps
                raise Exception(
                    'frequency isn\'t a positive number that is divisible by 10 and between 10000 and 20000')
            encryptor.lock_folder(password, folder=folder_path)
            # inserts to json file of setup files in our computer the filename, the password hash (sha256) and the requested frequency for the lock
            insert_into_sql(folder_path, freq, encryptor.generate_pbkdf2(password))
            print('done!!')
            break
        except Exception as e:
            print(e, file=sys.stderr)


def delete_from_sql():
    """

    :return: deletes all moved files from sql, in case they were moved from their location
    """
    conn = sqlite3.connect('folders.db')
    cursor = conn.execute('SELECT PATH FROM FOLDER_DATA')
    for row in cursor.fetchall():
        if not os.path.isfile(encryptor.insert_enc_tag(row[0]) + '.zip'):
            conn.execute('DELETE FROM FOLDER_DATA WHERE PATH=(?)', (row[0],))
    conn.commit()
    conn.close()


def main():
    """

    :return: setups the folder
    Note, only in case you want to override and existing file
    """
    delete_from_sql()
    while True:
        try:
            folder_path = os.path.abspath(input('enter folder name: '))
            if not os.path.isdir(folder_path):
                raise Exception('the  un-setup-ed folder doesn\'t exist')
            removed_folder = encryptor.insert_enc_tag(folder_path) + '.zip'
            if os.path.isfile(removed_folder):
                ans = ask_removal_of_folder()
                if not ans:
                    print('OK, please choose another folder')
                    continue
                else:
                    os.remove(removed_folder)
            sql_setup(folder_path)

            break
        except Exception as e:
            print(e, file=sys.stderr)


if __name__ == '__main__':
    main()
