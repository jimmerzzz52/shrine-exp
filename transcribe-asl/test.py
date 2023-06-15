# python3.10 -m venv handsy         
# source handsy/bin/activate 
import cv2
import mediapipe as mp
import numpy as np
import math

# Define mediapipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Define OpenCV capture object
cap = cv2.VideoCapture(0)

# Define the angles calculation function
def calculate_angles(points):
    # Define landmarks for each finger
    landmarks = {
        'thumb': [points[4], points[3], points[2], points[1]],
        'index': [points[8], points[7], points[6], points[5]],
        'middle': [points[12], points[11], points[10], points[9]],
        'ring': [points[16], points[15], points[14], points[13]],
        'pinky': [points[20], points[19], points[18], points[17]],
    }
    
    # Define joint indexes for each finger
    joints = {
        'thumb': (0, 1, 2),
        'index': (0, 1, 2),
        'middle': (0, 1, 2),
        'ring': (0, 1, 2),
        'pinky': (0, 1, 2)
    }
    
    # Calculate angles for each finger
    angles = {}
    for finger in landmarks.keys():
        if finger == 'thumb':
            # Thumb angle calculation is slightly different
            d1 = np.linalg.norm(np.array(landmarks[finger][joints[finger][0]]) - np.array(landmarks[finger][joints[finger][1]]))
            d2 = np.linalg.norm(np.array(landmarks[finger][joints[finger][1]]) - np.array(landmarks[finger][joints[finger][2]]))
            angle = math.degrees(math.acos((d1**2 + d2**2 - (d1 + d2)**2) / (2*d1*d2)))
            angles[finger] = angle
        else:
            # Calculate angle for each joint in the finger
            angles[finger] = []
            for i in range(len(joints[finger])-1):
                a = np.array(landmarks[finger][joints[finger][i]])
                b = np.array(landmarks[finger][joints[finger][i+1]])
                c = np.array(landmarks[finger][joints[finger][i+2]])
                radian_angle = math.acos(np.dot(b-a, c-b) / (np.linalg.norm(b-a) * np.linalg.norm(c-b) + 1e-8))
                angles[finger].append(math.degrees(radian_angle))
    
    return angles
t = 0
while True:
    # Capture video frame-by-frame
    ret, frame = cap.read()
    print(ret)
    print(frame)
    if not ret:
        break
    
    # Flip frame horizontally for easier user experience
    frame = cv2.flip(frame, 1)
    
    # Convert frame to RGB and pass to mediapipe hands module
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    t = t + 1