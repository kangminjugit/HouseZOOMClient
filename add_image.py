import cv2
import numpy as np

# 뱃지 클래스
class Badge:
    def __init__(self):
        medal = cv2.imread('HouseZOOMClient\medal.png')
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
    
# 폭탄 클래스
class Bomb:
    def __init__(self):
        me = cv2.imread('HouseZOOMClient/bomb.png',cv2.IMREAD_UNCHANGED)
        
        self.me = cv2.flip(me,1)
        
        _, self.mask = cv2.threshold(self.me[:,:,3], 1, 255, cv2.THRESH_BINARY)
        self.mask_inv = cv2.bitwise_not(self.mask)   
        
        self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)    
        h, w, c = me.shape
        self.h = h
        self.w = w
        self.c = c

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_bomb(self, frame):
        background_height, background_width, _ = frame.shape # 720,1280
        #x = background_height - self.h
        y = background_width - self.w
        
        roi = frame[10: 10+self.h, y: y+self.w]
        
        masked_me = cv2.bitwise_and(self.me, self.me, None, mask=self.mask)
        masked_roi = cv2.bitwise_and(roi, roi, None, mask=self.mask_inv)
    
        result = masked_me + masked_roi

        frame[10: 10+self.h, y: y+self.w] = result

        return frame   

# 하트 클래스
class Heart:
    def __init__(self):
        me = cv2.imread('HouseZOOMClient/heart.png',cv2.IMREAD_UNCHANGED)
        avatar = cv2.imread('HouseZOOMClient/rabbit.png',cv2.IMREAD_UNCHANGED)
        self.me = cv2.flip(me,1)
        
        _, self.mask = cv2.threshold(self.me[:,:,3], 1, 255, cv2.THRESH_BINARY)
        self.mask_inv = cv2.bitwise_not(self.mask)   
        
        self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)    
        h, w, c = me.shape
        self.h = h
        self.w = w
        self.c = c
        
        ah,aw,ac = avatar.shape
        self.ah = ah
        self.aw = aw
        self.ac = ac

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_heart(self, frame):
        
        background_height, background_width, _ = frame.shape # 720,1280
        x = background_height - self.ah
        y = background_width - self.w - self.aw
        
        roi = frame[x: x+self.h, y: y+self.w]
        
        masked_me = cv2.bitwise_and(self.me, self.me, None, mask=self.mask)
        masked_roi = cv2.bitwise_and(roi, roi, None, mask=self.mask_inv)

        result = masked_me + masked_roi

        frame[x: x+self.h, y: y+self.w] = result

        return frame    

# 아바타 클래스
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


    