import cv2
import mediapipe as mp
import numpy as np
from add_image import Heart


class gesture_analyzer:
    def __init__(self):
        self.idx = -1

        max_num_hands = 1  # 인식할 수 있는 손 개수

        self.gesture = {
            0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
            6: 'good', 7: 'bad', 8: 'heart', 9: 'ok'
        }  # 9가지 제스처, 제스처 데이터는 손가락 관절의 각도와 각각의 라벨을 뜻함.

        self.rps_gesture = {0: 'rock', 2: 'scissors', 5: 'paper'}  # 가위바위보

        self.heart = Heart()

        # MediaPipe hands model
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        # Gesture recognition model
        file = np.genfromtxt('train_data/gesture_data.csv', delimiter=',')
        self.angle = file[:, :-1].astype(np.float32)
        self.label = file[:, -1].astype(np.float32)
        self.knn = cv2.ml.KNearest_create()
        self.knn.train(self.angle, cv2.ml.ROW_SAMPLE, self.label)

    def detect(self, img):

        # 프레임을 좌우전환 후 RGB로 변환
        img = cv2.flip(img, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        result = self.hands.process(img)

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if result.multi_hand_landmarks is not None:
            for res in result.multi_hand_landmarks:
                joint = np.zeros((21, 3))
                for j, lm in enumerate(res.landmark):
                    joint[j] = [lm.x, lm.y, lm.z]

                # Compute angles between joints
                v1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 0,
                            13, 14, 15, 0, 17, 18, 19], :]  # Parent joint
                v2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                            13, 14, 15, 16, 17, 18, 19, 20], :]  # Child joint
                v = v2 - v1  # [20,3]
                # Normalize v
                v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                # Get angle using arcos of dot product
                angle = np.arccos(np.einsum('nt,nt->n',
                                            v[[0, 1, 2, 4, 5, 6, 8, 9, 10,
                                                12, 13, 14, 16, 17, 18], :],
                                            v[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]))  # [15,]

                angle = np.degrees(angle)  # Convert radian to degree

                # Inference gesture
                data = np.array([angle], dtype=np.float32)
                ret, results, neighbours, dist = self.knn.findNearest(data, 3)
                self.idx = int(results[0][0])

                # Draw gesture result 가위바위보
                # if idx in rps_gesture.keys():
                #cv2.putText(img, text=self.rps_gesture[idx].upper(), org=(int(res.landmark[0].x * img.shape[1]), int(res.landmark[0].y * img.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)

                # 숫자, 좋아요, 싫어요, 손하트, OK
                cv2.putText(img, text=self.gesture[self.idx].upper(), org=(int(res.landmark[0].x * img.shape[1]), int(
                    res.landmark[0].y * img.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)

                # self.mp_drawing.draw_landmarks(img, res, self.mp_hands.HAND_CONNECTIONS) # 손마디 랜드마크 표시

                if self.idx == 8:
                    img = cv2.flip(img, 1)
                    img = self.heart.add_heart(img)
                    img = cv2.flip(img, 1)
        # else:
            #img = cv2.flip(img, 1)

        img = cv2.flip(img, 1)
        return(img, self.idx)
