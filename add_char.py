import cv2
import numpy as np

# 뱃지 클래스
class Character:
    def __init__(self):
        me = cv2.imread('HouseZOOMClient/rabbit.png',cv2.IMREAD_UNCHANGED)
        self.me = cv2.flip(me,1)
        #self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)
        #self.gray = cv2.cvtColor(self.me, cv2.COLOR_BGR2GRAY)
        #_, self.mask_inv = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY_INV)
        _, self.mask = cv2.threshold(self.me[:,:,3], 1, 255, cv2.THRESH_BINARY)
        self.mask_inv = cv2.bitwise_not(self.mask)   
        self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)    
        h, w, c = me.shape
        self.h = h
        self.w = w
        self.c = c

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_char(self, frame):
        
        background_height, background_width, _ = frame.shape # 720,1280
        x = background_height - self.h
        y = background_width - self.w
        
        roi = frame[x: x+self.h, y: y+self.w]
        
        masked_me = cv2.bitwise_and(self.me, self.me, None, mask=self.mask)
        masked_roi = cv2.bitwise_and(roi, roi, None, mask=self.mask_inv)
        
        #roi_char = cv2.add(self.me, roi, mask = self.mask_inv)
        
        #result = cv2.add(roi_char, self.me)
        result = masked_me + masked_roi

        frame[x: x+self.h, y: y+self.w] = result

        return frame