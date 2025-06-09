from cv2_enumerate_cameras import enumerate_cameras
import cv2

for camera_info in enumerate_cameras():
    print(f'{camera_info.index}: {camera_info.name}')

cap = cv2.VideoCapture(camera_info.index, camera_info.backend)