import cv2
import mediapipe as mp
import time
from gesture.base import Gesture, to_hand_frame, Output
import numpy as np


def main():

    g = Gesture()  # Load outside to prevent reloading base gestures from disk

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic

    # access webcam
    cap = cv2.VideoCapture(0)
    # address = "http://192.168.15.35:8080/video"
    # cap.open(address)
    with mp_holistic.Holistic(
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.1,
        min_tracking_confidence=0.1,
        enable_segmentation=False,
        refine_face_landmarks=True,
        static_image_mode=False,
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
            # mp_drawing.draw_landmarks(
            #     frame,
            #     results.pose_landmarks,
            #     mp_holistic.POSE_CONNECTIONS,
            #     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
            # )
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

            mp_drawing.draw_axis(
                frame,
                np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                np.array([0.089, -0.089, 0]),
            )

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

            output: Output = g.predict(right_hand_data, left_hand_data, pose_data)
            print(output)

            draw_rotated_left_hand(
                frame,
                left_hand_data,
                mp_drawing,
                results.left_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_pose_landmarks_style(),
            )

            draw_rotated_right_hand(
                frame,
                right_hand_data,
                mp_drawing,
                results.right_hand_landmarks,
                mp_holistic.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_pose_landmarks_style(),
                # scale=1,
            )

            # base_points_in_hand_frame: np.array = to_hand_frame(
            #     np.genfromtxt(
            #         "./gesture/base_poses_hf/one_Transcription_Right_Hand.csv",
            #         delimiter=",",
            #     )[1:, 1:]
            # )

            # draw_rotated_right_hand(
            #     frame,
            #     base_points_in_hand_frame,
            #     mp_drawing,
            #     results.right_hand_landmarks,
            #     mp_holistic.HAND_CONNECTIONS,
            #     mp_drawing_styles.get_default_pose_landmarks_style(),
            #     scale=1,
            # )
            rec_out_static_print = ['Nothing']
            try:
                rec_out_static_print = [
                    f"{i}, Conf: {output.static_gestures_confidence[i]:.3f}"
                    for i in output.static_gestures
                ]
            except:
                print("Something went wrong")

            for i, rec in enumerate(rec_out_static_print):
                cv2.putText(
                    frame,
                    rec,
                    (20, 170 + i * 30),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (0, 255, 0),
                    2,
                )
            cv2.putText(
                frame,
                f"FPS: {int(fps)}   Static: {output.static_gestures[0]}",
                (20, 70),
                cv2.FONT_HERSHEY_PLAIN,
                3,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Movement: {output.movement_gestures}",
                (20, 110),
                cv2.FONT_HERSHEY_PLAIN,
                3,
                (0, 255, 0),
                2,
            )

            # cv2.putText(
            #     frame,
            #     f"Check point: {g.check_point}",
            #     (20, 140),
            #     cv2.FONT_HERSHEY_PLAIN,
            #     1,
            #     (0, 255, 0),
            #     2,
            # )

            cv2.imshow("MediaPipe Holistic", frame)

    #         print(fps)
    # release everything
    cap.release()
    cv2.destroyAllWindows()


def draw_rotated_left_hand(
    frame,
    left_hand_data,
    mp_drawing,
    landmarks,
    connections,
    landmark_drawing_spec,
    scale=1 / 3,
):
    """
    Draw the left hand landmarks in the top left corner of the frame.
    """
    # Draw left hand smaller in corner
    if landmarks:
        left_hand_data = to_hand_frame(left_hand_data, norm=False).dot(
            np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
        )
        left_hand_data_small = left_hand_data * scale
        left_hand_data_small[:, 0] = (
            left_hand_data_small[:, 0] - left_hand_data_small[:, 0].min()
        )
        left_hand_data_small[:, 1] = (
            left_hand_data_small[:, 1] - left_hand_data_small[:, 1].max() + 1
        )
        # left_hand_data_small[:, 2] = left_hand_data_small[:, 2] - left_hand_data_small[:, 2].min()
        draw_landmark(
            frame,
            left_hand_data_small,
            mp_drawing,
            landmarks,
            connections,
            landmark_drawing_spec,
        )


def draw_rotated_right_hand(
    frame,
    right_hand_data,
    mp_drawing,
    landmarks,
    connections,
    landmark_drawing_spec,
    scale=1 / 3,
):
    """
    Draw the right hand landmarks in the top right corner of the frame.
    """
    # Draw right hand smaller in corner
    if landmarks:
        right_hand_data = to_hand_frame(right_hand_data, norm=False).dot(
            np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
        )
        right_hand_data_small = right_hand_data * scale
        right_hand_data_small[:, 0] = (
            right_hand_data_small[:, 0] - right_hand_data_small[:, 0].max() + 1
        )
        right_hand_data_small[:, 1] = (
            right_hand_data_small[:, 1] - right_hand_data_small[:, 1].max() + 1
        )
        # right_hand_data_small[:, 2] = right_hand_data_small[:, 2] - right_hand_data_small[:, 2].min()
        draw_landmark(
            frame,
            right_hand_data_small,
            mp_drawing,
            landmarks,
            connections,
            landmark_drawing_spec,
        )


def draw_landmark(
    frame, data, mp_drawing, landmarks, connections, landmark_drawing_spec
):
    """
    Draw the landmark data on the frame.
    """
    for i in range(len(landmarks.landmark)):
        landmarks.landmark[i].x = data[i, 0].astype(float)
        landmarks.landmark[i].y = data[i, 1].astype(float)
        landmarks.landmark[i].z = data[i, 2].astype(float)
    mp_drawing.draw_landmarks(
        frame,
        landmarks,
        connections,
        landmark_drawing_spec,
    )


if __name__ == "__main__":
    main()
