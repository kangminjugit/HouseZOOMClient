# from pickle import TRUE
# from typing_extensions import Self
import socketio
import argparse
import cv2
import pyvirtualcam
from pyvirtualcam import PixelFormat
import numpy as np
import keyboard
from PIL import Image

from gesture_Analyze import gesture_analyzer
# from  multiprocessing import pool
from add_image import Badge
from add_image import Character
from Quiz.quiz import QuizHandler

from face_Detect import face_detecter
from gesture_Analyze import gesture_analyzer
from multi_hand_Analyze import multi_hand_analyzer

from threading import Timer


class ClassHandle:
    def __init__(self, studentId, classId, accessToken, name):
        self.studentId = studentId
        self.classId = classId
        self.accessToken = accessToken

        self.quizOn = False

        self.sio = socketio.Client()
        # self.sio.connect('http://3.35.141.211:4040')
        self.sio.connect('http://localhost:4040')
        self.sio.emit('student_join_class', {
            'data': {
                'studentId': studentId,
                'classId': classId,
                'name': name
            }
        })

        self.sio.on('get_point', self.pointHandler)
        self.sio.on('get_badge', self.badgeHandler)
        self.sio.on('get_ox_quiz', self.oxQuizHandler)
        self.sio.on('get_choice_quiz', self.choiceQuizHandler)
        self.sio.on('quiz_timeout', self.quizTimeoutHandler)

        self.start_quiz = False
        self.showQuizResult = False
        self.show_quiz_submit_msg = False
        self.quizAnswer = -1
        self.badgeQueue = []

        self.quizHandler = QuizHandler()
        self.frameProcess()

    def pointHandler(self, data):
        print(data)

    def badgeHandler(self, data):
        print(data)
        if len(self.badgeQueue) == 2:
            self.badgeQueue.pop(0)
        self.badgeQueue.append({'is_quiz': False, 'text': '-{} 시간 업적-\n{}'.format(
            data['data']['subject'], data['data']['description'])})

    def oxQuizHandler(self, data):
        print(data)
        self.quizOn = True
        self.quizText = data['data']['problem']
        self.is_ox = True

    def choiceQuizHandler(self, data):
        print(data)
        self.quizOn = True
        self.quizText = data['data']['problem']
        self.multiChoices = data['data']['multiChoices']
        self.is_ox = False

    def submitQuizHandler(self, quizAnswer):
        if quizAnswer == 'O' or quizAnswer == 'X':
            self.sio.emit('submit_quiz', {
                'data': {
                    'classId': self.classId,
                    'studentId': self.studentId,
                    'answer': True if quizAnswer == 'O' else False
                }
            })
        else:
            self.sio.emit('submit_quiz', {
                'data': {
                    'classId': self.classId,
                    'studentId': self.studentId,
                    'answer': quizAnswer
                }
            })

    def quizTimeoutHandler(self, data):
        print(data)
        if 'studentAnswer' in data['data']:
            answer = data['data']['answer']
            is_correct = data['data']['is_correct']
            is_ox = data['data']['is_ox']

            self.quizOn = False

            self.quizHandler.set_quiz_result(answer, is_correct, is_ox)

            self.showQuizResult = True
            self.show_quiz_submit_msg = False

            # 정답이면 뱃지 추가
            if is_correct:
                if len(self.badgeQueue) == 2:
                    self.badgeQueue.pop(0)
                self.badgeQueue.append(
                    {'is_quiz': True, 'text': '-업적-\n퀴즈 정답'})
        else:
            answer = data['data']['answer']
            is_correct = data['data']['is_correct']
            is_ox = data['data']['is_ox']
            self.quizOn = False
            self.quizHandler.set_quiz_result(answer, is_correct, is_ox)
            self.showQuizResult = True
            self.show_quiz_submit_msg = False

    def showQuizResultToggle(self):
        self.showQuizResult = False

    def frameProcess(self):
        print('start virtual camera')
        self.run_camera()

    def startQuizToggle(self):
        self.start_quiz = False

    def showQuizSubmitMsgToggle(self):
        self.show_quiz_submit_msg = False

    def run_camera(self):
        hand_detect = False
        wake = False
        GA = gesture_analyzer()
        FD = face_detecter()
        MHA = multi_hand_analyzer()  # 두손 제스처 인식

        parser = argparse.ArgumentParser()
        parser.add_argument("--camera", type=int, default=0,
                            help="ID of webcam device (default: 0)")
        parser.add_argument("--fps", action="store_true",
                            help="output fps every second")
        parser.add_argument(
            "--filter", choices=["shake", "none"], default="shake")
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

        # 뱃지, 아바타 틀 만들기
        badge = Badge()
        avatar = Character(self.studentId, self.accessToken)

        # 퀴즈 답 세팅
        multi_idx = idx = -1

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

                # 얼굴 눈 찾기
                frame, sleep = FD.detect(frame,wake)
                
                if sleep: #졸음 감지했을 때
                    frame, idx = GA.detect(frame)
                    if idx == 5: #손바닥을 보임
                        wake = True
                else:
                    wake = False 

                # 퀴즈가 시작되면 손 인식 시작
                # 퀴즈가 끝나면 손 인식 종료
                if hand_detect != self.quizOn:
                    hand_detect = not hand_detect
                    frame = self.quizHandler.start_quiz(frame)

                    # 퀴즈 시작을 알리는 표시 3초 동안 보여줌
                    self.start_quiz = True
                    startQuizSignOver = Timer(3.0, self.startQuizToggle)
                    startQuizSignOver.start()

                if hand_detect:
                    # 퀴즈 시작 표시
                    if self.start_quiz:
                        frame = self.quizHandler.start_quiz(frame)
                        if self.is_ox == False:
                            self.quizHandler.set_multichoice_quiz(
                                frame, self.quizText, self.multiChoices)
                        else:
                            self.quizHandler.set_ox_quiz(frame, self.quizText)

                    # 퀴즈 시작 표시 후 퀴즈 문제 공개
                    else:
                        frame = self.quizHandler.show_quiz(frame)

                        if self.is_ox == False:
                            frame, multi_idx = GA.detect(frame)
                        else:
                            frame, multi_idx = GA.detect(frame)
                            frame, idx = MHA.detect(frame)  # idx 6 = X, 7 = O

                    # 답으로 예상되는 손 제스쳐 인식
                    if self.is_ox:
                        if idx == 'O' or idx == 'X':
                            self.quizAnswer = idx
                    else:
                        if (1 <= multi_idx and multi_idx <= 5):
                            self.quizAnswer = multi_idx

                    # 답 표시를 했고 good 표시함
                    if self.quizAnswer != -1 and multi_idx == 6:
                        self.quizOn = False
                        self.submitQuizHandler(self.quizAnswer)
                        self.quizAnswer = -1

                        self.show_quiz_submit_msg = True

                if self.show_quiz_submit_msg:
                    frame = self.quizHandler.show_quiz_submit_msg(frame)

                elif self.showQuizResult:
                    self.showQuizSubmitMsgToggle()
                    frame = self.quizHandler.show_quiz_result(frame)
                    showQuizResult = Timer(3.0, self.showQuizResultToggle)
                    showQuizResult.start()

                # 뱃지 그리기
                if len(self.badgeQueue) >= 1:
                    frame = badge.add_badge(frame, self.badgeQueue)
                # 아바타 그리기
                frame = avatar.add_char(frame)

                # 이미지 좌우반전
                # frame = cv2.flip(frame, 1)

                # Send to virtual cam
                cam.send(frame)

                # Wait until it's time for the next frame.
                cam.sleep_until_next_frame()

                # # q 누르면 종료
                # if keyboard.is_pressed('q'):
                #     break

        vc.release()
