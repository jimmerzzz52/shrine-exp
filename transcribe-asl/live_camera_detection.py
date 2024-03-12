import cv2
import mediapipe as mp
import time
from gesture.base import Gesture
import numpy as np

import cv2


def main():

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic

    # access webcam
    cap = cv2.VideoCapture(0)
    # address = "http://192.168.15.35:8080/video"
    # cap.open(address)
    with mp_holistic.Holistic(
        model_complexity=1,
        smooth_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        enable_segmentation=True,
        refine_face_landmarks=False,
    ) as holistic:
        while True:
            # pull frame
            start = time.time()
            ret, frame = cap.read()
            frame = cv2.resize(frame, (1080, 720))
            # mirror frame
            # frame = cv2.flip(frame, 1)
            # display frame
            if cv2.waitKey(1) == ord("q"):
                break

            results = holistic.process(frame)

            # print(results.pose_landmarks)

            # Draw landmark annotation on the frame.
            frame.flags.writeable = True
            # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_holistic.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )
            mp_drawing.draw_landmarks(
                frame,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )

            mp_drawing.draw_landmarks(
                frame,
                results.right_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            )

            mp_drawing.draw_axis(frame, np.eye(3), np.zeros(3)) 
            # This is important, it draws the axis of the camera. 

            end = time.time()

            fps = 1 / (end - start)
            # TODO: Insert pose_recognized code here... Import module and run command.
            right_hand_data = None
            pose_data = None
            left_hand_data = None
            if results.right_hand_landmarks:
                # TODO: Move this repetitive code into a function or module somewhere...
                right_hand_raw = list(results.right_hand_landmarks.landmark)
                right_hand_data = np.array(
                    [[value.x, value.y, value.z] for value in right_hand_raw]
                )
            if results.pose_landmarks:
                pose_raw = list(results.pose_landmarks.landmark)
                pose_data = np.array(
                    [[value.x, value.y, value.z] for value in pose_raw]
                )
            if results.left_hand_landmarks:
                left_hand_raw = list(results.left_hand_landmarks.landmark)
                left_hand_data = np.array(
                    [[value.x, value.y, value.z] for value in left_hand_raw]
                )

            g = Gesture(right_hand_data, left_hand_data, pose_data)
            recognition_output = g.fit()

            cv2.putText(
                frame,
                f"FPS: {int(fps)}   Gesture Recognized: {recognition_output}",
                (20, 70),
                cv2.FONT_HERSHEY_PLAIN,
                3,
                (0, 255, 0),
                2,
            )
            
            cv2.imshow("MediaPipe Holistic", frame)

    #         print(fps)
    # release everything
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
