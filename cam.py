import argparse
import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import numpy as np
import keyboard
from PIL import Image
from add_image import Badge
from add_image import Character

from face_Detect import face_detecter
from gesture_Analyze import gesture_analyzer
from multi_hand_Analyze import multi_hand_analyzer

def run_camera():   
    hand_detect = False
    two_hand_detect = False
    wake = False
    GA = gesture_analyzer() #제스처 인식
    MHA = multi_hand_analyzer() #두손 제스처 인식
    FD = face_detecter() #얼굴 감지
    

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
    
    fps_out = 30

    # 이미지 틀 만들기
    badge = Badge()
    avatar = Character()

    with pyvirtualcam.Camera(width, height, fps_out, fmt=PixelFormat.BGR, print_fps=args.fps) as cam:
        print(f'Virtual cam started: {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

        while True:
            # Read frame from webcam.
            ret, frame = vc.read()
            if not ret:
                raise RuntimeError('Error fetching frame')

            # 이미지 그레이스케일로 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 얼굴 눈 찾기    
            frame, sleep = FD.detect(frame,wake)
            
            if sleep:
                frame, idx = GA.detect(frame)
                if idx == 5:
                    wake = True
            else:
                wake = False        
            
            # 제스처 분석 (h 누르면 제스처 분석 시작)
            if keyboard.is_pressed('h'):
                hand_detect = not hand_detect
            if hand_detect:
                frame, idx = GA.detect(frame)

            if keyboard.is_pressed('k'):
                two_hand_detect = not two_hand_detect
            if two_hand_detect:
                frame, idx = MHA.detect(frame) #idx 6 = X, 7 = O
                            
            #뱃지 그리기
            frame = badge.add_badge(frame)
            #아바타 그리기
            frame = avatar.add_char(frame)
            
            #이미지 좌우반전
            frame = cv2.flip(frame, 1)

            # Send to virtual cam
            cam.send(frame)

            # Wait until it's time for the next frame.
            cam.sleep_until_next_frame()

            # q 누르면 종료
            if keyboard.is_pressed('q'):
                break
            
    vc.release() 