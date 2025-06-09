import cv2
# import numpy as np
# import os
from gaze_tracking import GazeTracking
from datetime import datetime
import yaml

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('matrix/matrix.yml')
haar_cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_cascade_path);

font = cv2.FONT_HERSHEY_COMPLEX

import sqlite3

with open('old_schedule.yaml', 'r', encoding ="UTF-8") as file:
    schedule = yaml.safe_load(file)

current_weekday = datetime.now().isoweekday()
today_schedule = schedule[10][5][current_weekday]
lines = ""
for row in today_schedule:
    lines += f"\n{row['num']} {row['start_time']}:{row['end_time']} {row['title']} ({row['room']})"

# print(lines)
# exit()

# Создаем подключение к базе данных (файл my_database.db будет создан)
connection = sqlite3.connect('database_people.db')

# инициация счетчика id
name = 0


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


connection.row_factory = dict_factory
cursor = connection.cursor()
# имена соответствуют id. Пример ==> Anton: id=1,  etc
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
# print(users)
# exit()

# Инициализация и старт трансляции видео с камеры
camera = cv2.VideoCapture(1)
camera.set(3, 1280)  # ширина видео
camera.set(4, 720)  # высота видео

# Установка минимального размера окна видео для распознавания лица
minW = 0.1 * camera.get(3)
minH = 0.1 * camera.get(4)

gaze = GazeTracking()

while True:

    ret, img = camera.read()
    # img = cv2.flip(img, -1) # Flip vertically
    gaze.refresh(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )

    for (x, y, w, h) in faces:

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        # Коэфициент должен быть меньше 100 -> "0" лучшее совпадение
        if (confidence < 100):
            name = [f"{user['first_name']} {user['last_name']}" for user in users if user['id'] == id][0]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            name = "неизвестный"
            confidence = "  {0}%".format(round(100 - confidence))

        if gaze.is_center():
            name += 'Смотрит в центр'
            cv2.putText(img, str(lines), (15, 15), font, 0.4, (255, 255, 0), 1)

        # name += lines

        cv2.putText(img, str(name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
        # cv2.putText(img, str(confidence), (5, 5), font, 1, (255, 255, 0), 1)

    cv2.imshow('cameraera', img)

    k = cv2.waitKey(10) & 0xff  # Нажать 'ESC' для выхода
    if k == 27:
        break

# Очистка информации
print("\n Выход из программы и очистка материалов")
camera.release()
cv2.destroyAllWindows()
