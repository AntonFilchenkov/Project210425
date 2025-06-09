import time
import cv2
import pygame
from icecream import ic
import requests
import json
from gaze_tracking import GazeTracking
from datetime import datetime
import yaml
import sqlite3

# Инициализация распознавания лиц
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('matrix/matrix.yml')
haar_cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haar_cascade_path)
font = cv2.FONT_HERSHEY_COMPLEX


def get_weather():
    API = '75af176011419f43080b33d44c0c47f8'
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q=moscow&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
    else:
        temp = None
    return temp


with open('news.yaml', 'r', encoding="UTF-8") as file:
    news = yaml.safe_load(file)
today = datetime.now().strftime("%d.%m.%y")
news_today = [v for k, v in news.items() if k.strip() == today][0]

with open('old_schedule.yaml', 'r', encoding="UTF-8") as file:
    schedule = yaml.safe_load(file)

connection = sqlite3.connect('database_people.db')
connection.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
cursor = connection.cursor()
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()


def draw_text(text, x, y):
    for line in text.splitlines():
        text_surface = pygame_font.render(line, True, WHITE)
        screen.blit(text_surface, (x, y))
        y += pygame_font.get_linesize()


def draw_info(name, schedule, date_time, temp, news, x, y):
    pygame_font = pygame.font.Font(None, 36)
    current_weekday = date_time.isoweekday()
    today_schedule = schedule[current_weekday]

    text_surface = pygame_font.render(f"Сегодня {date_time.strftime('%d.%m.%y %H:%M')}", True, WHITE)
    screen.blit(text_surface, (x, y))
    y += 2 * pygame_font.get_linesize()

    if temp:
        text_surface = pygame_font.render(f"Температура сейчас {round(temp, 0)} C", True, WHITE)
        screen.blit(text_surface, (x, y))
        y += 2 * pygame_font.get_linesize()

    text_surface = pygame_font.render(f"Добрый день, {name} !", True, WHITE)
    screen.blit(text_surface, (x, y))
    y += 2 * pygame_font.get_linesize()

    start_time = date_time.combine(date_time.date(), datetime.strptime("00:00", "%H:%M").time())
    for row in today_schedule:
        line = f"{row['num']} {row['start_time']} - {row['end_time']} {row['title']} ({row['room']})"
        end_time = date_time.combine(date_time.date(), datetime.strptime(row['end_time'], "%H:%M").time())
        if start_time < date_time <= end_time:
            color = (255, 0, 0)
        else:
            color = WHITE
        text_surface = pygame_font.render(line, True, color)
        screen.blit(text_surface, (x, y))
        y += pygame_font.get_linesize()
        start_time = end_time

    y += pygame_font.get_linesize()
    text_surface = pygame_font.render("Новость дня:", True, WHITE)
    screen.blit(text_surface, (x, y))
    y += 2 * pygame_font.get_linesize()
    for line in news_today.strip().splitlines():
        text_surface = pygame_font.render(line, True, WHITE)
        screen.blit(text_surface, (x, y))
        y += pygame_font.get_linesize()


# Инициализация камеры и трекера взгляда
# cv2.VideoCapture(0) - основная камера
# cv2.VideoCapture(1) - дополнительная
camera_id=1
camera = cv2.VideoCapture(camera_id)
camera.set(3, 640)
camera.set(4, 480)
minW = 0.1 * camera.get(3)
minH = 0.1 * camera.get(4)
gaze = GazeTracking()

# Инициализация Pygame
pygame.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
pygame_font = pygame.font.Font(None, 36)
screen_width = 768
screen_height = 1024
screen = pygame.display.set_mode((screen_width, screen_height), flags = pygame.NOFRAME, display=1)
pygame.display.set_caption("YAML Data Display")

# Переменные для управления отображением
last_center_time = 0
display_duration = 1  # 1 секунды взгляда для активации
display_time = 10  # 10 секунд показа информации
should_display = False
display_start_time = 0
current_name = ""

while True:
    ret, img = camera.read()
    gaze.refresh(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )

    current_time = time.time()

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        if confidence < 100:
            current_name = [f"{user['first_name']} {user['last_name']}" for user in users if user['id'] == id][0]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            current_name = "неизвестный"
            confidence = "  {0}%".format(round(100 - confidence))

        cv2.putText(img, str(current_name), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

    # Логика отображения информации
    if gaze.is_center():
        if last_center_time == 0:
            last_center_time = current_time
        elif current_time - last_center_time >= display_duration and not should_display:
            should_display = True
            display_start_time = current_time
            temp = get_weather()
    else:
        last_center_time = 0
        # Не сбрасываем should_display здесь, чтобы дать возможность показать информацию полные 10 секунд

    # Очистка экрана
    screen.fill(BLACK)

    # Отображение информации, если нужно
    if should_display:
        if current_time - display_start_time <= display_time:
            draw_info(current_name, schedule[10][5], datetime.now(), temp, news_today, 50, 50)
        else:
            should_display = False
            last_center_time = 0

    cv2.imshow('camera', img)
    pygame.display.flip()

    k = cv2.waitKey(10) & 0xff
    if k == 27:
        break

# Очистка
pygame.quit()
camera.release()
cv2.destroyAllWindows()