import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import requests
import urllib.request

# 뱃지 클래스


class Badge:
    def __init__(self):
        self.font = ImageFont.truetype(os.path.join(
            'Quiz/Font', 'SuseongDotum.ttf'), 20, encoding="UTF-8")
        self.quiz_badge = Image.open('Image/quiz_badge.jpg')
        self.badge = Image.open('Image/badge.jpg')

        self.qw, self.qh = self.quiz_badge.size
        self.quiz_draw = ImageDraw.Draw(self.quiz_badge)

        self.w, self.h = self.badge.size
        self.draw = ImageDraw.Draw(self.badge)

    # 기존 프레임에 뱃지를 붙이는 함수

    def add_badge(self, frame, badgeQueue):
        startW = 10

        for badgeElem in badgeQueue:
            if badgeElem['is_quiz']:
                tw, th = self.quiz_draw.textsize(
                    badgeElem['text'], self.font)
                self.quiz_draw.text((self.qw//2-tw//2, self.qh//2-th//2), badgeElem['text'], fill='black',
                                    font=self.font, align='center')
                flipped_badge_img = self.quiz_badge.transpose(
                    Image.FLIP_LEFT_RIGHT)
                frame[10:10+self.qh, startW:startW+self.qw] = flipped_badge_img
            else:
                tw, th = self.quiz_draw.textsize(
                    badgeElem['text'], self.font)
                self.draw.text((self.w//2-tw//2, self.h//2-th//2), badgeElem['text'], fill='black',
                               font=self.font, align='center')
                flipped_badge_img = self.badge.transpose(
                    Image.FLIP_LEFT_RIGHT)
                frame[10:10+self.h, startW:startW+self.w] = flipped_badge_img
            startW = startW+self.w+10

        return frame


# 폭탄 클래스
class Bomb:
    def __init__(self):
        me = cv2.imread('Image/bomb.png', cv2.IMREAD_UNCHANGED)

        self.me = cv2.flip(me, 1)

        _, self.mask = cv2.threshold(
            self.me[:, :, 3], 1, 255, cv2.THRESH_BINARY)
        self.mask_inv = cv2.bitwise_not(self.mask)

        self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)
        h, w, c = me.shape
        self.h = h
        self.w = w
        self.c = c

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_bomb(self, frame):
        background_height, background_width, _ = frame.shape  # 720,1280
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
        me = cv2.imread('Image/heart.png', cv2.IMREAD_UNCHANGED)
        avatar = cv2.imread('Image/rabbit.png', cv2.IMREAD_UNCHANGED)
        self.me = cv2.flip(me, 1)

        _, self.mask = cv2.threshold(
            self.me[:, :, 3], 1, 255, cv2.THRESH_BINARY)
        self.mask_inv = cv2.bitwise_not(self.mask)

        self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)
        h, w, c = me.shape
        self.h = h
        self.w = w
        self.c = c

        ah, aw, ac = avatar.shape
        self.ah = ah
        self.aw = aw
        self.ac = ac

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_heart(self, frame):

        background_height, background_width, _ = frame.shape  # 720,1280
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
    def __init__(self, studentId, accessToken):
        headers = {"Authorization": "Bearer %s" % accessToken}
        response = requests.get(
            'http://3.35.141.211:3000/api/avatar/cur-item?studentId={}'.format(studentId), headers=headers).json()

        itemArr = response['data']['items']

        # me = cv2.imread('Image/avatar_body.png', cv2.IMREAD_UNCHANGED)

        avatar_body = Image.open('Image/avatar_body.png')

        for item in itemArr:
            urllib.request.urlretrieve(item['image'], 'item_image.png')
            # object = bucket.Object(item['image'].split('https://housezoombucket.s3.ap-northeast-2.amazonaws.com/', 1)[1])
            # item_img = Image.open(BytesIO(requests.get(item['image'])))
            item_img = Image.open('item_image.png')
            avatar_body.paste(item_img, (0, 0), item_img)

        avatar_body.save('avatar.png')
        me = cv2.imread('avatar.png', cv2.IMREAD_UNCHANGED)
        # me = cv2.cvtColor(me, cv2.COLOR_RGBA2RGB)
        self.me = cv2.flip(me, 1)

        #self.me = cv2.cvtColor(self.me, cv2.COLOR_BGRA2BGR)
        #self.gray = cv2.cvtColor(self.me, cv2.COLOR_BGR2GRAY)
        #_, self.mask_inv = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY_INV)
        _, self.mask = cv2.threshold(
            self.me[:, :, 3], 1, 255, cv2.THRESH_BINARY)
        self.mask_inv = cv2.bitwise_not(self.mask)
        h, w, c = me.shape
        self.h = h
        self.w = w
        self.c = c

    # 기존 프레임에 뱃지를 붙이는 함수
    def add_char(self, frame):

        background_height, background_width, _ = frame.shape  # 720,1280
        x = background_height - self.h
        y = background_width - self.w

        roi = frame[x: x+self.h, y: y+self.w]

        masked_me = cv2.bitwise_and(self.me, self.me, None, mask=self.mask)
        masked_roi = cv2.bitwise_and(roi, roi, None, mask=self.mask_inv)

        masked_me = cv2.cvtColor(masked_me, cv2.COLOR_RGBA2RGB)
        #roi_char = cv2.add(self.me, roi, mask = self.mask_inv)

        #result = cv2.add(roi_char, self.me)
        result = masked_me + masked_roi

        frame[x: x+self.h, y: y+self.w] = result

        return frame
