import cv2
import math
import timeit
import pygame
import mediapipe as mp
from add_image import Bomb

class face_detecter:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_face_mesh = mp.solutions.face_mesh
        
        self.TIMER_FLAG = False #Flag to activate 'start_closing' variable, which measures the eyes closing time.
        self.ALARM_FLAG = False #Flag to check if alarm has ever been triggered.
        self.start_closing = timeit.default_timer()
        self.COUNTER = 0
        self.ALARM_COUNT = 0 #Number of times the total alarm rang.
        self.RUNNING_TIME = 0
        self.PREV_TERM = 0 #Variable to measure the time eyes were being opened until the alarm rang.

        self.sleep = False
        
        # Left eyes indices 
        self.LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
        # right eyes indices
        self.RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]
        
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.bomb = Bomb()
        self.alarm = Alarm()
    
    def detect(self,image,wake):
        image = cv2.flip(image, 1)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image)

        # Draw the face mesh annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
        if results.multi_face_landmarks:
            
            #얼굴 인식하고 있을 때 눈 감지
            mesh_coords = self.landmarksDetection(image, results, False)
            ratio = self.blinkRatio(image, mesh_coords, self.RIGHT_EYE, self.LEFT_EYE)
            #cv2.putText(image, f'ratio {ratio}', (100, 100), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))

            if ratio > 5.5:
                if not self.TIMER_FLAG:
                    self.start_closing = timeit.default_timer()
                    self.TIMER_FLAG = True
                self.COUNTER += 1

                if self.COUNTER >= 200:
                    self.sleep = True
                    image = self.draw_bomb(image)
                    mid_closing = timeit.default_timer()
                    closing_time = round((mid_closing-self.start_closing),3)

                    if closing_time >= self.RUNNING_TIME:
                        if self.RUNNING_TIME == 0 :
                            CUR_TERM = timeit.default_timer()
                            OPENED_EYES_TIME = round((CUR_TERM - self.PREV_TERM),3)
                            self.PREV_TERM = CUR_TERM
                            self.RUNNING_TIME = 1.75
                        
                        self.alarm.sound_alarm()        
                        self.RUNNING_TIME += 40
                        self.ALARM_FLAG = True
                        self.ALARM_COUNT += 1


                #cv2.putText(image, 'Blink', (200, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
            
            elif (ratio <= 5.5) and (not wake) and (self.sleep): #눈을 뜨고 있지만 그 전까지 자고 있었고 손바닥을 보여주지 않음
                image = self.draw_bomb(image)
            
            elif (ratio <= 5.5) and (wake): #눈도 뜨고 있고 손바닥을 보였을 때
                self.alarm.alarm_Off()
                self.sleep = False
                self.COUNTER = 0
                self.TIMER_FLAG = False
                self.RUNNING_TIME = 0
                self.ALARM_FLAG = False

            
            """   
            #얼굴 눈 윤곽선 그리기
            for face_landmarks in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles
                    .get_default_face_mesh_contours_style()) 
            """           
                      
        else:
            #폭탄 그리기
            image = cv2.flip(image, 1)  
            image = self.bomb.add_bomb(image)
            image = cv2.flip(image, 1)  
            
        image = cv2.flip(image, 1)          
        return(image,self.sleep)
    
    def draw_bomb(self,image):
        image = cv2.flip(image, 1)  
        image = self.bomb.add_bomb(image)
        image = cv2.flip(image, 1)
        return image               
    
    def landmarksDetection(self, img, results, draw=False):
        img_height, img_width= img.shape[:2]
        # list[(x,y), (x,y)....]
        mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
        # returning the list of tuples for each landmarks 
        return mesh_coord
    
    # Euclaidean distance
    def euclaideanDistance(self, point, point1):
        x, y = point
        x1, y1 = point1
        distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
        return distance

    def blinkRatio(self, img, landmarks, right_indices, left_indices):
        # Right eyes 
        # horizontal line 
        rh_right = landmarks[right_indices[0]]
        rh_left = landmarks[right_indices[8]]
        # vertical line 
        rv_top = landmarks[right_indices[12]]
        rv_bottom = landmarks[right_indices[4]]
        
        # LEFT_EYE 
        # horizontal line 
        lh_right = landmarks[left_indices[0]]
        lh_left = landmarks[left_indices[8]]
        # vertical line 
        lv_top = landmarks[left_indices[12]]
        lv_bottom = landmarks[left_indices[4]]
        
        # Finding Distance Right Eye
        rhDistance = self.euclaideanDistance(rh_right, rh_left) 
        rvDistance = self.euclaideanDistance(rv_top, rv_bottom)
        #cv2.putText(img, f'rvDistance{rvDistance}', (100, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
        #cv2.putText(img, f'rhDistance{rhDistance}', (100, 150), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
        
        # Finding Distance Left Eye
        lvDistance = self.euclaideanDistance(lv_top, lv_bottom)
        lhDistance = self.euclaideanDistance(lh_right, lh_left)
        # Finding ratio of LEFT and Right Eyes
        reRatio = rhDistance/(rvDistance+0.1)
        leRatio = lhDistance/(lvDistance+0.1)
        ratio = (reRatio+leRatio)/2
        return ratio


class Alarm:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.music.load('HouseZOOMClient/timer.MP3')

    def sound_alarm(self) :
        pygame.mixer.music.play()
            
    def alarm_Off(self):
        pygame.mixer.music.stop() 
        pygame.mixer.music.rewind()      