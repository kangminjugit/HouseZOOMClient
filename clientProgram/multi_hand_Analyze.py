import cv2
import mediapipe as mp
import numpy as np
from add_image import Heart


class multi_hand_analyzer:
    def __init__(self):
        max_num_hands = 2  # 인식할 수 있는 손 개수

        # 2가지의 제스처, 제스처 데이터는 손가락 관절의 각도와 각각의 라벨을 뜻한다.
        self.gesture = {6: 'X', 7: 'O'}

        # MediaPipe hands model
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        # Gesture recognition model
        file = np.genfromtxt(
            'train_data/gesture_data_2.csv', delimiter=',')
        self.angle = file[:, :-1].astype(np.float32)
        self.label = file[:, -1].astype(np.float32)
        self.knn = cv2.ml.KNearest_create()
        self.knn.train(self.angle, cv2.ml.ROW_SAMPLE, self.label)

    def detect(self, img):

        idx = -1

        # 프레임을 좌우전환 후 RGB로 변환
        img = cv2.flip(img, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        check = np.zeros(shape=(4, 3))
        lv3 = np.zeros(shape=(4, 3))
        rv3 = np.zeros(shape=(4, 3))

        result = self.hands.process(img)

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if result.multi_hand_landmarks is not None:
            for num, hand in enumerate(result.multi_hand_landmarks):
                if result.multi_handedness[num].classification[0].label == "Left":
                    joint = np.zeros((21, 3))
                    for j, lm in enumerate(hand.landmark):
                        joint[j] = [lm.x, lm.y, lm.z]

                    # Compute angles between joints
                    lv1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11,
                                 0, 13, 14, 15, 0, 17, 18, 19], :]  # Parent joint
                    lv2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                 13, 14, 15, 16, 17, 18, 19, 20], :]  # Child joint
                    lv3 = joint[[5, 6, 7, 8], :]
                    lv = lv2 - lv1  # [20,3]
                    # Normalize v
                    lv = lv / np.linalg.norm(lv, axis=1)[:, np.newaxis]

                    # Get angle using arcos of dot product
                    angle = np.arccos(np.einsum('nt,nt->n',
                                                lv[[0, 1, 2, 4, 5, 6, 8, 9, 10,
                                                    12, 13, 14, 16, 17, 18], :],
                                                lv[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]))  # [15,]

                    angle = np.degrees(angle)  # Convert radian to degree
                    l_data = np.array([angle], dtype=np.float32)

                if result.multi_handedness[num].classification[0].label == "Right":
                    joint = np.zeros((21, 3))
                    for j, lm in enumerate(hand.landmark):
                        joint[j] = [lm.x, lm.y, lm.z]

                    # Compute angles between joints
                    rv1 = joint[[0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11,
                                 0, 13, 14, 15, 0, 17, 18, 19], :]  # Parent joint
                    rv2 = joint[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                                 13, 14, 15, 16, 17, 18, 19, 20], :]  # Child joint
                    rv3 = joint[[5, 6, 7, 8], :]
                    rv = rv2 - rv1  # [20,3]
                    # Normalize v
                    rv = rv / np.linalg.norm(rv, axis=1)[:, np.newaxis]

                    # Get angle using arcos of dot product
                    angle = np.arccos(np.einsum('nt,nt->n',
                                                rv[[0, 1, 2, 4, 5, 6, 8, 9, 10,
                                                    12, 13, 14, 16, 17, 18], :],
                                                rv[[1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19], :]))  # [15,]

                    angle = np.degrees(angle)  # Convert radian to degree
                    r_data = np.array([angle], dtype=np.float32)

                if (len(result.multi_handedness) == 2) and (not np.array_equal(rv3, check)) and (not np.array_equal(lv3, check)):
                    lrv = rv3 - lv3  # [4,3]
                    lrv = lrv / np.linalg.norm(lrv, axis=1)[:, np.newaxis]
                    lr_angle = np.arccos(np.einsum('nt,nt->n',
                                                   lrv[[0, 1, 2], :],
                                                   lrv[[1, 2, 3], :]))  # [3,]

                    lr_angle = np.degrees(lr_angle)  # Convert radian to degree
                    lr_data = np.array([lr_angle], dtype=np.float32)

                    data_1 = np.concatenate((l_data, r_data), axis=1)
                    data = np.append(data_1, lr_data)
                    data = data.reshape(1, -1)

                    ret, results, neighbours, dist = self.knn.findNearest(
                        data, 3)
                    idx = int(results[0][0])

                    # 숫자, 좋아요, 싫어요, 손하트, OK
                    cv2.putText(img, text=self.gesture[idx].upper(), org=(int(hand.landmark[0].x * img.shape[1]), int(
                        hand.landmark[0].y * img.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)

                # self.mp_drawing.draw_landmarks(img, res, self.mp_hands.HAND_CONNECTIONS) # 손마디 랜드마크 표시

        # else:
            #img = cv2.flip(img, 1)

        img = cv2.flip(img, 1)

        if idx == -1:
            return (img, -1)
        else:
            return(img, self.gesture[idx])
