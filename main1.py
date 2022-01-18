import psycopg2
from config import *
import telebot
import re
import os
import subprocess

# bot API token
# use environment variables
API_TOKEN = os.environ["API_TELEGRAM"]
bot = telebot.TeleBot(API_TOKEN, parse_mode=None)

def main():
    try:
        # connect to exist database
        connection = psycopg2.connect(
    #        host=host, # для использования БД по локальной сети
            user=user,
    #        port = port, # для использования БД по локальной сети
            password=password,
            database=db_name
        )
        connection.autocommit = True
        print("INFO connected")

            # print vesrion server
        def get_vesrion_serever():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT version();"
                )
            v = 'Server version ' + cursor.fetchone()
            return v

        def create_new_table(name):
            # create a new table
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""CREATE TABLE {name} (
                    id serial PRIMARY KEY,
                    first_name varchar(50),
                    nick_name varchar(50),
                    user_id int,
                    link_audio varchar,
                    link_image varchar);"""
                )
                print("Table was created")

        def ins_new_data(db_name, first_name, nick_name, user_id):
            # Insert new data in database
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""INSERT INTO {db_name} (first_name, nick_name, user_id) VALUES
                    ('{first_name}', '{nick_name}', '{user_id}');"""
                )
                print("DATA WAS INSERT")
                cursor.execute (
                    f"""SELECT * FROM {db_name}
                        ORDER BY id DESC limit 1"""
                )
                return cursor.fetchall()

        def upd_database():
            # update exist data base
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE tg_users
                    SET user_id = 2;"""
                )
                print("DATABASE WAS UPDATED")

        def get_data(data,table):
            # get data
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT {data} FROM {table};"""
                )
                #print(cursor.fetchall())
                return cursor.fetchall()

        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            bot.reply_to(message, "How are you doing?")

        # создаём новую БД с именем, которое указано после /create
        @bot.message_handler(commands=['create'])
        def send_welcome(message):
            text = message.text.split()
            text = create_new_table(text[1])
            bot.reply_to(message, "DATA BASE WAS CREATED" + str(text))

        # делаем запрос к БД где первое слово после /q будет что ище, а второе в какой БД
        @bot.message_handler(commands=['q'])
        def send_welcome(message):
            text = message.text.split()
            text = get_data(text[1],text[2])
            text1 = ''
            text1 += '\n\n'.join(map(str, text))
            bot.send_message(message.chat.id, str(text1))

        @bot.message_handler(commands=['ins'])
        def send_welcome(message):
            text = message.text.split()
            ret = ins_new_data(text[1], message.from_user.first_name, message.from_user.username, message.from_user.id)
            bot.send_message(message.chat.id, str(ret))

        # сохраняем локально аудио-файл
        @bot.message_handler(content_types=['voice'])
        def voice_processing(message):
            # делаем запрос на кол-во уже голосовых этого пользователя
            with connection.cursor() as cursor:
                cursor.execute (
                        f"""SELECT count(id) FROM tg_users
                            WHERE user_id = '{message.from_user.id}'"""
                    )
                count = cursor.fetchone()

            # удаляем лишние символы из ответа
            count = re.sub('[(),]', '', str(count))
            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # задаём имя файла
            file_name = 'audio_message_' + str(count)

            # записываем файл
            with open(file_name + '.oga', 'wb') as new_file:
                new_file.write(downloaded_file)

            # конвертация аудио в wav 16kHz
            subprocess.run(['ffmpeg', '-i', file_name + '.oga', '-ar', '16000', file_name + '.wav'])

            # запись пути к файлу в БД
            with connection.cursor() as cursor:
             cursor.execute (
                     f"""INSERT INTO tg_users (first_name, nick_name, user_id, link_audio) VALUES
                 ('{message.from_user.first_name}','{message.from_user.username}','{message.from_user.id}','{os.path.abspath(file_name + '.wav')}');"""
                 )

            # delete file .oga from server
            print(f"DELETE {file_name}.oga")
            os.remove(file_name + '.oga')

        bot.infinity_polling()

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostrgeSQL connectuion closed")

if __name__ == "__main__":
    main()
