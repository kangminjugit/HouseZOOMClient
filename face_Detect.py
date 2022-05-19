import cv2
import math
import mediapipe as mp
from add_image import Bomb

class face_detecter:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Left eyes indices 
        self.LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
        # right eyes indices
        self.RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]
        
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.bomb = Bomb()
    
    def detect(self,image):
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
            mesh_coords = self.landmarksDetection(image, results, False)
            ratio = self.blinkRatio(image, mesh_coords, self.RIGHT_EYE, self.LEFT_EYE)
            #cv2.putText(image, f'ratio {ratio}', (100, 100), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
 
            if ratio >5.5:
                #CEF_COUNTER +=1
                cv2.putText(image, 'Blink', (200, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
                      
        else:
            #뱃지 그리기
            image = cv2.flip(image, 1)  
            image = self.bomb.add_bomb(image)
            image = cv2.flip(image, 1)  
            
        image = cv2.flip(image, 1)          
        return(image) 
    
    def landmarksDetection(self, img, results, draw=False):
        img_height, img_width= img.shape[:2]
        # list[(x,y), (x,y)....]
        mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
        #if draw :
            #[cv.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]

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
        
        # Finding Distance Left Eye
        lvDistance = self.euclaideanDistance(lv_top, lv_bottom)
        lhDistance = self.euclaideanDistance(lh_right, lh_left)
        # Finding ratio of LEFT and Right Eyes
        reRatio = rhDistance/rvDistance
        leRatio = lhDistance/lvDistance
        ratio = (reRatio+leRatio)/2
        return ratio