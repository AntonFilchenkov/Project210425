import cv2
import os
import sqlite3

camera = cv2.VideoCapture(0)
camera.set(3, 640)  # ширина видео
camera.set(4, 480)  # высота видео

face_finder = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Ввод уникального номера для каждого ученика
# face_id = input('\n Введите ID пользователя и нажмите Enter: ')
user_data = {}

user_data['first_name'] = input('\n Введите имя пользователя и нажмите Enter: ')
user_data['last_name'] = input('\n Введите фамилию пользователя и нажмите Enter: ')
user_data['patronymic_name'] = input('\n Введите отчество пользователя и нажмите Enter: ')
user_data['grade'] = int(input('\n Введите номер параллели пользователя и нажмите Enter: '))
user_data['class_number'] = int(input('\n Введите номер класса пользователя и нажмите Enter: '))
user_data['tg_id'] = input('\n Введите телеграм пользователя и нажмите Enter: ')
# user_data['first_name'] = 'first'
# user_data['last_name'] = 'last'
# user_data['patronymic_name'] = 'patronymic'
# user_data['grade'] = 1
# user_data['class_number'] = 2



def create_user(connection, user_data):
    cursor = connection.cursor()
    a = cursor.execute(
        'INSERT INTO users (first_name, last_name, patronymic_name, grade, class_number) VALUES (?, ?, ?, ?, ?)',
        (user_data['first_name'], user_data['last_name'], user_data['patronymic_name'], user_data['grade'], user_data['class_number']),
    )
    # print(type(a))
    # print(a)
    connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    return user_id


connection = sqlite3.connect('database_people.db')
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
face_id = create_user(connection, user_data)
connection.close()
# exit()

print("\n Смотрите в камеру и ждите инициализации...")
# Настройка инициализации
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
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        count += 1

        # Сохранение фотографий  в папку dataset
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff  # Нажать 'ESC' для выхода
    if k == 27:
        break
    elif count >= 30:  # Спустя 30 сников лица - программа заканчивает собирать данные
        break

# Окончание работы
print("\n Выход из программы и очистка материалов")
camera.release()
cv2.destroyAllWindows()
