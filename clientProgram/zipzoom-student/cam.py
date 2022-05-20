import argparse
import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import numpy as np
import keyboard
from PIL import Image
from add_badge import Badge
from gesture_Analyze import gesture_analyzer


def run_camera():
    # haarcascade 불러오기
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')

    hand_detect = False
    GA = gesture_analyzer()

    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0,
                        help="ID of webcam device (default: 0)")
    parser.add_argument("--fps", action="store_true",
                        help="output fps every second")
    parser.add_argument("--filter", choices=["shake", "none"], default="shake")
    args = parser.parse_args()

    # Set up webcam capture.
    vc = cv2.VideoCapture(args.camera)

    if not vc.isOpened():
        raise RuntimeError('Could not open video source')

    pref_width = 1280
    pref_height = 720
    pref_fps_in = 30
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
    vc.set(cv2.CAP_PROP_FPS, pref_fps_in)

    # Query final capture device values (may be different from preferred settings).
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_in = vc.get(cv2.CAP_PROP_FPS)
    print(f'Webcam capture started ({width}x{height} @ {fps_in}fps)')

    fps_out = 30

    # 뱃지 틀 만들기
    badge = Badge()

    with pyvirtualcam.Camera(width, height, fps_out, fmt=PixelFormat.BGR, print_fps=args.fps) as cam:
        print(
            f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

        while True:
            # Read frame from webcam.
            ret, frame = vc.read()
            if not ret:
                raise RuntimeError('Error fetching frame')

            # 이미지 그레이스케일로 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 얼굴 눈 찾기 + 사각형 그리기
            frame = detect(face_cascade, eye_cascade, gray, frame)

            # 제스처 분석 (h 누르면 제스처 분석 시작)
            if keyboard.is_pressed('h'):
                hand_detect = not hand_detect
            if hand_detect:
                frame = GA.detect(frame)

            # 뱃지 그리기
            frame = badge.add_badge(frame)

            # Send to virtual cam
            cam.send(frame)

            # Wait until it's time for the next frame.
            cam.sleep_until_next_frame()

            # q 누르면 종료
            if keyboard.is_pressed('q'):
                break

    vc.release()


def detect(face_cascade, eye_cascade, gray, frame):

    # 등록한 Cascade classifier 를 이용하여 얼굴 찾기
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=3,
        minSize=(20, 20),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # 얼굴에 사각형을 그리고 눈 찾기
    for (x, y, w, h) in faces:
        # 얼굴: 이미지 프레임에 (x,y)에서 시작하여, (x+넓이, y+길이)까지의 사각형을 그림 (색 255 255 255 , 굵기 2)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        # 이미지를 얼굴 크기 만큼 잘라서 그레이스케일이미지(face_gray)와 컬러이미지(face_color)를 만듦
        face_gray = gray[y:y + h, x:x + w]
        face_color = frame[y:y + h, x:x + w]

        # 등록한 Cascade classifier 를 이용 눈을 찾음 (얼굴 영역에서만)
        eyes = eye_cascade.detectMultiScale(
            face_gray,
            1.1,
            5
        )

        # 눈: 이미지 프레임에 (ex,ey)에서 시작하여, (ex+넓이, ey+길이)까지의 사각형을 그림 (색 50 50 50 , 굵기 2)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(face_color, (ex, ey),
                          (ex + ew, ey + eh), (50, 50, 50), 2)

    return frame
