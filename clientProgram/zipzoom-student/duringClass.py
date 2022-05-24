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

from threading import Timer


class ClassHandle:
    def __init__(self, studentId, classId, accessToken):
        self.studentId = studentId
        self.classId = classId
        self.accessToken = accessToken

        self.quizOn = False

        self.sio = socketio.Client()
        self.sio.connect('http://localhost:4040')
        self.sio.emit('student_join_class', {
            'data': {
                'studentId': studentId,
                'classId': classId
            }
        })

        self.sio.on('get_point', self.pointHandler)
        self.sio.on('get_badge', self.badgeHandler)
        self.sio.on('get_ox_quiz', self.oxQuizHandler)
        self.sio.on('get_choice_quiz', self.choiceQuizHandler)
        self.sio.on('quiz_timeout', self.quizTimeoutHandler)

        self.start_quiz = False
        self.showQuizResult = False
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

    def choiceQuizHandler(self, data):
        print(data)
        self.quizOn = True
        self.quizText = data['data']['problem']
        self.multiChoices = data['data']['multiChoices']

    def submitQuizHandler(self, quizAnswer):
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
            studentAnswer = data['data']['studentAnswer']
            answer = data['data']['answer']
            is_correct = data['data']['is_correct']

            self.quizOn = False

            self.quizHandler.set_quiz_result(studentAnswer, answer, is_correct)

            self.showQuizResult = True

            # 정답이면 뱃지 추가
            if is_correct:
                if len(self.badgeQueue) == 2:
                    self.badgeQueue.pop(0)
                self.badgeQueue.append(
                    {'is_quiz': True, 'text': '-업적-\n퀴즈 정답'})
        else:
            answer = data['data']['answer']
            is_correct = data['data']['is_correct']
            self.quizOn = False
            self.quizHandler.set_quiz_result('', answer, is_correct)
            self.showQuizResult = True

    def showQuizResultToggle(self):
        self.showQuizResult = False

    def frameProcess(self):
        print('start virtual camera')
        self.run_camera()

    def startQuizToggle(self):
        self.start_quiz = not self.start_quiz

    def run_camera(self):
        hand_detect = False
        GA = gesture_analyzer()
        FD = face_detecter()

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

        # 이미지 틀 만들기
        badge = Badge()
        avatar = Character(self.studentId, self.accessToken)

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
                frame = FD.detect(frame)

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
                    frame, idx = GA.detect(frame)

                    # 퀴즈 시작 표시
                    if self.start_quiz:
                        frame = self.quizHandler.start_quiz(frame)
                        if self.multiChoices:
                            self.quizHandler.set_quiz(
                                frame, self.quizText, self.multiChoices)
                        else:
                            self.quizHandler.set_quiz(frame, self.quizText)

                    # 퀴즈 시작 표시 후 퀴즈 문제 공개
                    else:
                        frame = self.quizHandler.show_quiz(frame)

                    # 답으로 예상되는 손 제스쳐 인식
                    if 1 <= idx and idx <= 5:
                        self.quizAnswer = idx
                        frame = self.quizHandler.show_quiz_submit_msg(frame)

                    # 답 표시를 했고 good 표시함
                    if self.quizAnswer != -1 and idx == 6:
                        self.quizOn = False
                        self.submitQuizHandler(self.quizAnswer)
                        self.quizAnswer = -1

                if self.showQuizResult:
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

    def detect(self, face_cascade, eye_cascade, gray, frame):

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
