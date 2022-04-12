import argparse
import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import numpy as np
from PIL import Image
from add_badge import Badge

def run_camera():
    # haarcascade 불러오기
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0, help="ID of webcam device (default: 0)")
    parser.add_argument("--fps", action="store_true", help="output fps every second")
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

    fps_out = 20


    # 뱃지 틀 만들기
    badge = Badge()

    with pyvirtualcam.Camera(width, height, fps_out, fmt=PixelFormat.BGR, print_fps=args.fps) as cam:
        print(f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

        # Shake two channels horizontally each frame.
        channels = [[0, 1], [0, 2], [1, 2]]

        while True:
            # Read frame from webcam.
            ret, frame = vc.read()
            if not ret:
                raise RuntimeError('Error fetching frame')

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=3,
                minSize=(20,20)
            )

            for(x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,255,255), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

            frame = badge.add_badge(frame)

            # Send to virtual cam.
            cam.send(frame)

            # Wait until it's time for the next frame.
            cam.sleep_until_next_frame()

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break

    cam.release()