import cv2

# 뱃지 클래스
class Badge:
    def __init__(self):
        medal = cv2.imread('medal.png')
        self.medal = cv2.cvtColor(medal, cv2.COLOR_BGRA2BGR)
        self.medal = cv2.flip(self.medal,1)
        h, w, c = medal.shape
        self.h = h
        self.w = w
        self.c = c

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_badge(self, frame):
        roi = frame[10:10 + self.h, 10:10 + self.w]

        # 단순 bitwise or로 뱃지를 붙여서 뱃지가 희미하게 보임
        result = cv2.bitwise_or(self.medal, roi)
        frame[10:10 + self.h, 10:10 + self.w] = result

        return frame