import cv2
import numpy as np
from PIL import Image
import os

# Папка с фото для обучения матрицы
path = 'dataset'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

# Функция для получения фото
def get_images(path):

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

print ("\n Обучение матрицы на основе фотографий. Это займет некоторое время. Ожидайте...")
faces,ids = get_images(path)
recognizer.train(faces, np.array(ids))

# Cохранение модели обучения в матрицу matrix/matrix.yml
recognizer.write('matrix/matrix.yml')

# Вывод количества фотографий по котором прошло обучение и выход
print("\n {0} фотографий прошли обучение. Выход из программы".format(len(np.unique(ids))))
