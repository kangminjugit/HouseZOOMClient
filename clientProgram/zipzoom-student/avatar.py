import cv2

# 뱃지 클래스
class Avatar:
    def __init__(self):
        avatar = cv2.imread('Image/avatar_body.png')
        self.avatar = cv2.cvtColor(avatar, cv2.COLOR_BGRA2BGR)
        self.avatar = cv2.flip(self.avatar,1)
        h, w, c = avatar.shape
        self.h = h
        self.w = w
        self.c = c

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_avatar(self, frame):
        roi = frame[10:10 + self.h, 10:10 + self.w]

        # 단순 bitwise or로 뱃지를 붙여서 뱃지가 희미하게 보임
        result = cv2.bitwise_or(self.avatar, roi)
        frame[10:10 + self.h, 10:10 + self.w] = result

        return frame