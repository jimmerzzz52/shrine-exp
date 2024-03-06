import cv2
import mediapipe as mp
import time


import cv2

def main():
    
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic
    
    # access webcam
    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(
        model_complexity=0,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        enable_segmentation=True,
        refine_face_landmarks=True,
    ) as holistic:
        while True:
            # pull frame
            ret, frame = cap.read()
            # mirror frame
            frame = cv2.flip(frame, 1)
            # display frame
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) == ord('q'):
                break
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame)
            
            # print(results.pose_landmarks)

            # Draw landmark annotation on the frame.
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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
                landmark_drawing_spec=mp_drawing_styles
                .get_default_pose_landmarks_style())
            cv2.imshow("MediaPipe Holistic", frame)
            fps = 1/(end-start)
            # TODO: Insert pose_recognized code here... Import module and run command.
            cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
            
#         print(fps)
    # release everything
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
   main()