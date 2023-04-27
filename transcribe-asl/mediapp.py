import cv2
import mediapipe as mp
import datetime
from math import atan2, degrees, sqrt
from itertools import zip_longest

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic


def get_coordinator(word):
    cap = cv2.VideoCapture(f'https://www.handspeak.com/{word.get("url")}')

    pose_csv = 'time,index,x,y,z\n'
    left_hand_csv = 'time,index,x_angle,y_angle,z_angle,x,y,z\n'
    right_hand_csv = 'time,index,x_angle,y_angle,z_angle,x,y,z\n'
    
    with mp_holistic.Holistic(
        model_complexity=1, 
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        enable_segmentation=True,
        refine_face_landmarks=True
    ) as holistic:  
        start_time = datetime.datetime.now()
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                cap.release()
                continue

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            
            if results.pose_landmarks:
                for index, data_point in enumerate(results.pose_landmarks.landmark):
                    pose_csv = pose_csv + \
                        f'{datetime.datetime.now() - start_time},' + \
                        f'{index},' + \
                        f'{data_point.x},' + \
                        f'{data_point.y},' + \
                        f'{data_point.z} \n'

            if results.right_hand_landmarks:
                data = list(zip_longest(results.right_hand_landmarks.landmark,
                            results.right_hand_landmarks.landmark[1:]))
                for index, value in enumerate(data):
                    if value[0] and value[1]:
                        
                        v = [value[1].x-value[0].x, value[1].y-value[0].y, value[1].z-value[0].z]
                        x_angle = degrees(atan2(v[1], v[2]))
                        y_angle = degrees(
                            atan2(-v[0], sqrt(v[1]**2 + v[2]**2)))
                        z_angle = degrees(atan2(v[0], -v[1]))

                        right_hand_csv = right_hand_csv + \
                            f'{datetime.datetime.now() - start_time},' + \
                            f'{index},' + \
                            f'{360 + x_angle if x_angle < 0 else x_angle},' + \
                            f'{360 + y_angle if y_angle < 0 else y_angle},' + \
                            f'{360 + z_angle if z_angle < 0 else z_angle},' + \
                            f'{data_point.x},' + \
                            f'{data_point.y},' + \
                            f'{data_point.z} \n'
                    else:
                        right_hand_csv = right_hand_csv + \
                            f'{datetime.datetime.now() - start_time},' + \
                            f'{index},' + \
                            f'{None},' + \
                            f'{None},' + \
                            f'{None},' + \
                            f'{data_point.x},' + \
                            f'{data_point.y},' + \
                            f'{data_point.z} \n'

            if results.left_hand_landmarks:
                data = list(zip_longest(results.left_hand_landmarks.landmark,
                            results.left_hand_landmarks.landmark[1:]))
                for index, value in enumerate(data):
                    if value[0] and value[1]:

                        v = [value[1].x-value[0].x, value[1].y-value[0].y, value[1].z-value[0].z]
                        x_angle = degrees(atan2(v[1], v[2]))
                        y_angle = degrees(
                            atan2(-v[0], sqrt(v[1]**2 + v[2]**2)))
                        z_angle = degrees(atan2(v[0], -v[1]))

                        left_hand_csv = left_hand_csv + \
                            f'{datetime.datetime.now() - start_time},' + \
                            f'{index},' + \
                            f'{360 + x_angle if x_angle < 0 else x_angle},' + \
                            f'{360 + y_angle if y_angle < 0 else y_angle},' + \
                            f'{360 + z_angle if z_angle < 0 else z_angle},' + \
                            f'{data_point.x},' + \
                            f'{data_point.y},' + \
                            f'{data_point.z} \n'
                    else:
                        left_hand_csv = left_hand_csv + \
                            f'{datetime.datetime.now() - start_time},' + \
                            f'{index},' + \
                            f'{None},' + \
                            f'{None},' + \
                            f'{None},' + \
                            f'{data_point.x},' + \
                            f'{data_point.y},' + \
                            f'{data_point.z} \n'

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles
                .get_default_pose_landmarks_style())
            
            mp_drawing.draw_landmarks(
                image,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles
                .get_default_pose_landmarks_style())
            
            mp_drawing.draw_landmarks(
                image,
                results.right_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles
                .get_default_pose_landmarks_style())

            cv2.imshow('MediaPipe Holistic', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()

    file = open(f"{word.get('title')}_Transcription_Pose.csv", "w")
    file.write(pose_csv)
    file.close()

    file = open(f"{word.get('title')}_Transcription_Left_Hand.csv", "w")
    file.write(left_hand_csv)
    file.close()

    file = open(f"{word.get('title')}_Transcription_Right_Hand.csv", "w")
    file.write(right_hand_csv)
    file.close()