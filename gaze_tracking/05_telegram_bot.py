import logging
import os
import sqlite3
import sys
import time
from datetime import datetime

import cv2
import telebot
import yaml
from icecream import ic
from telebot import types
import numpy as np
from PIL import Image


keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

# Подключение к БД(файлу)
connection = sqlite3.connect("database_people.db")
connection.row_factory = sqlite3.Row  # Enable dictionary-like access

# указываем токен для доступа к боту
bot = telebot.TeleBot(
    "7723406641:AAEpzwFy1ZLwpjyD3q4qNqYcyIL19EDnq_c", colorful_logs=True
)

# Get bot info (including username)
# bot_info = bot.get_me()

# # Generate the bot link
# bot_link = f"https://t.me/{bot_info.username}"
# print(f"Bot link: {bot_link}")
# exit()

# приветственный текст
start_txt = "Привет! Это бот для создания учетной записи."


# обрабатываем старт бота
# @bot.message_handler(commands=['start'])
# def start(message):
#     # выводим приветственное сообщение
#     option_1 = types.KeyboardButton(text='/add')
#     keyboard.add(option_1)
#     bot.send_message(message.from_user.id, start_txt, parse_mode='Markdown', reply_markup=keyboard)


def send_news(news) -> None:
    cursor = connection.cursor()
    query = """
    SELECT DISTINCT 
        u.*
    FROM 
        users u
    JOIN 
        users_settings s ON u.id = s.user_id
    WHERE 
        s.news = 1 
        AND u.telegram_id IS NOT NULL;
    """
    for user in cursor.execute(query):
        ic(dict(user))
        bot.send_message(int(user["telegram_id"]), news.strip().replace("\n", " "))


with open("news.yaml", "r", encoding="UTF-8") as file:
    news = yaml.safe_load(file)
# ic(news)
today = datetime.now().strftime("%d.%m.%y")
news_today = [v for k, v in news.items() if k.strip() == today][0]
ic(news_today)
TG_ID_MAXIM = 240989205
send_news(news_today)
# exit()


def create_user(user_data: dict) -> int:
    """
    Добавляет пользователя в БД (таблица `users`)

    :param connection: Подключение к БД
    :param user_data: Данные пользователя
    :return: ИД пользователя в БД
    """

    # FIXME: Соединение должно открываться на старте бота, закрываться при его отсановке, а в функцию попадать параметром
    with sqlite3.connect("database_people.db") as connection:
        cursor = connection.cursor()
        a = cursor.execute(
            "INSERT INTO users (first_name, last_name, patronymic_name, grade, class_number, telegram_id) VALUES (:first_name, :last_name, :patronymic_name, :grade, :class_number, :telegram_id)",
            user_data,
        )
        # print(type(a))
        # print(a)
        connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return user_id


# FIXME: должно стартовать добавление пользователя сразу при /start
@bot.message_handler(commands=["start"])
def enter_first_name(message):
    # выводим приветственное сообщение
    bot.send_message(
        message.from_user.id,
        "создание пользователя\nВведите имя",
        parse_mode="Markdown",
    )
    # user_tg_id = message.chat.id()
    bot.register_next_step_handler(message, enter_last_name)
    # print(user_tg_id)


# @bot.message_handler()
def enter_last_name(message):
    user_data = {
        "telegram_id": message.from_user.id,
        "first_name": message.text,
    }
    ic(user_data)
    bot.send_message(message.from_user.id, "Введите фамилию", parse_mode="Markdown")
    bot.register_next_step_handler(message, enter_patronymic_name, user_data=user_data)


def enter_patronymic_name(message, user_data: dict[str, any]):
    user_data["last_name"] = message.text
    ic(user_data)
    bot.send_message(message.from_user.id, "Введите отчество", parse_mode="Markdown")
    bot.register_next_step_handler(message, enter_grade, user_data=user_data)


def enter_grade(message, user_data: dict[str, any]):
    user_data["patronymic_name"] = message.text
    ic(user_data)
    bot.send_message(message.from_user.id, "Введите параллель", parse_mode="Markdown")
    bot.register_next_step_handler(message, enter_class_number, user_data=user_data)


def enter_class_number(message, user_data: dict[str, any]):
    user_data["grade"] = message.text
    ic(user_data)
    bot.send_message(message.from_user.id, "Введите класс", parse_mode="Markdown")
    bot.register_next_step_handler(message, save_user, user_data=user_data)



def create_user_dataset(face_id):
    camera = cv2.VideoCapture(1)
    camera.set(3, 640)  # ширина видео
    camera.set(4, 480)  # высота видео
    face_finder = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    count = 0
    while True:
        ret, img = camera.read()
        # img = cv2.flip(img, -1) # flip video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # faces = face_finder.detectMultiScale(gray, 1.3, 5)
        faces = face_finder.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            count += 1

            # Сохранение фотографий  в папку dataset
            cv2.imwrite(
                "dataset/User." + str(face_id) + "." + str(count) + ".jpg",
                gray[y : y + h, x : x + w],
            )

            cv2.imshow("image", img)

        # k = cv2.waitKey(100) & 0xff  # Нажать 'ESC' для выхода
        # if k == 27:
        #     break
        if count >= 30:
            # Спустя 30 сников лица - программа заканчивает собирать данные
            break

    camera.release()
    cv2.destroyAllWindows()

def get_images(path, detector):

    image_paths = [os.path.join(path,f) for f in os.listdir(path)]
    face_sample=[]
    ids = []

    for image_path in image_paths:

        PIL_img = Image.open(image_path).convert('L') # преобразование в градации серого
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(image_path)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            face_sample.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return face_sample,ids
def train_matrix():
    # Папка с фото для обучения матрицы
    path = 'dataset'

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    ic("\n Обучение матрицы на основе фотографий. Это займет некоторое время. Ожидайте...")
    faces, ids = get_images(path, detector)
    recognizer.train(faces, np.array(ids))

    # Cохранение модели обучения в матрицу matrix/matrix.yml
    recognizer.write('matrix/matrix.yml')

    # Вывод количества фотографий по котором прошло обучение и выход
    ic("\n {0} фотографий прошли обучение. Выход из программы".format(len(np.unique(ids))))


def save_user(message, user_data: dict[str, any]):
    user_data["class_number"] = int(message.text)
    ic(user_data)
    ic(create_user(user_data))
    face_id = create_user(user_data)
    bot.send_message(
        message.from_user.id, f"Посмотрите в камеру", parse_mode="Markdown"
    )
    # time.sleep(2000)
    create_user_dataset(face_id)
    train_matrix()
    bot.send_message(
        message.from_user.id, f"Вы зарегистрированы", parse_mode="Markdown"
    )
    # bot.send_message(message.from_user.id, "Введите класс", parse_mode='Markdown')
    # bot.register_next_step_handler(message, save_user, user_data=user_data)


# def save_user(message, user_data: dict[str, any]):
#     user_data['class_number'] = int(message.text)
#     ic(user_data)


# обрабатываем любой текстовый запрос
# @bot.message_handler(content_types=['text'])


@bot.message_handler(commands=["settings"])
def set_setting_user_news(message):
    # выводим приветственное сообщение
    # user_tg_id = message.chat.id()
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("Да")
    item2 = types.KeyboardButton("Нет")
    item3 = types.KeyboardButton("Назад")

    # Добавляем кнопки в клавиатуру
    markup.add(item1, item2, item3)

    # Отправляем сообщение с кастомной клавиатурой
    bot.send_message(
        message.chat.id,
        "Хотите ли Вы получать новости? Выберите одну из кнопок:",
        parse_mode="Markdown",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, set_user_setting_messages)
    # print(user_tg_id)


def set_user_setting_messages(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("Да")
    item2 = types.KeyboardButton("Нет")
    item3 = types.KeyboardButton("Назад")

    # Добавляем кнопки в клавиатуру
    markup.add(item1, item2, item3)

    user_settings = {
        "telegram_id": message.from_user.id,
    }
    if message.text == "Да":
        user_settings["news"] = True
    elif message.text == "Нет":
        user_settings["news"] = False
    else:
        ic(message.text)
    ic(user_settings)
    bot.send_message(
        message.from_user.id,
        "Хотите ли Вы получать сообщения от пользователей? Выберите одну из кнопок:",
        parse_mode="Markdown",
        reply_markup=markup,
    )
    bot.register_next_step_handler(
        message, save_user_settings_handle, user_settings=user_settings
    )


def save_user_settings_handle(message, user_settings=dict[str, any]):
    if message.text == "Да":
        user_settings["message"] = True
    elif message.text == "Нет":
        user_settings["message"] = False
    else:
        ic(message.text)
    save_user_settings(user_settings)


def save_user_settings(user_settings=dict[str, any]) -> None:
    ic(user_settings)
    # FIXME: Соединение должно открываться на старте бота, закрываться при его отсановке, а в функцию попадать параметром
    with sqlite3.connect("database_people.db") as connection:
        cursor = connection.cursor()
        a = cursor.execute(
            """
                UPDATE users_settings
                    SET
                        news = :news,
                        message = :message
                    WHERE
                        user_id = (SELECT id FROM users WHERE telegram_id = :telegram_id);
            """,
            user_settings,
        )
        # print(type(a))
        # print(a)
        connection.commit()
        assert cursor.rowcount == 1
        cursor.close()


if __name__ == "__main__":
    from icecream import ic
    from datetime import datetime

    with sqlite3.connect("database_people.db") as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            patronymic_name TEXT,
            grade INTEGER NOT NULL,
            class_number INTEGER NOT NULL
        )
        ''')
        cursor.close()
        connection.commit()

    while True:
        # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
        try:
            ic(datetime.now())
            bot.polling(non_stop=True, interval=3)
            ic(datetime.now())
        # если возникла ошибка — сообщаем про исключение и продолжаем работу
        except Exception as e:
            print("❌❌❌❌❌ Сработало исключение! ❌❌❌❌❌")
# запускаем бота
