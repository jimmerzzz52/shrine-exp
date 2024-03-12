import cv2
import mediapipe as mp
import datetime
from pathlib import Path
from multiprocessing import Pool
from cap_from_youtube import cap_from_youtube

from math import atan2, degrees, sqrt
from itertools import zip_longest
import os
import glob
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

# Excute in parallel?
execute_parallel = False

images = glob.glob("images_of_gestures/*.jpg")


def transcribe_word(image_file):
    name = image_file.split("/")[-1].split(".")[0]
    pose_name = f"{name}_Transcription_Pose"
    left_name = f"{name}_Transcription_Left_Hand"
    rigth_name = f"{name}_Transcription_Right_Hand"

    if (
        not os.path.isfile(f"./gesture/base_poses_hf/{pose_name}.csv")
        or not os.path.isfile(f"./gesture/base_poses_hf/{left_name}.csv")
        or not os.path.isfile(f"./gesture/base_poses_hf/{rigth_name}.csv")
    ):
        image = cv2.imread(f"{image_file}")

        print("Capturing feed and registering pose points")
        with mp_holistic.Holistic(
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            enable_segmentation=True,
            refine_face_landmarks=True,
        ) as holistic:
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            pose_csv = "index,x,y,z\n"
            left_hand_csv = "index,x,y,z\n"
            right_hand_csv = "index,x,y,z\n"
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)

            if results.pose_landmarks:
                for index, data_point in enumerate(results.pose_landmarks.landmark):

                    pose_csv = (
                        pose_csv
                        + f"{index},"
                        + f"{data_point.x},"
                        + f"{data_point.y},"
                        + f"{data_point.z}\n"
                    )

            if results.right_hand_landmarks:
                data = list(results.right_hand_landmarks.landmark)
                for index, value in enumerate(data):
                    right_hand_csv = (
                        right_hand_csv
                        + f"{index},"
                        + f"{value.x},"
                        + f"{value.y},"
                        + f"{value.z} \n"
                    )

            if results.left_hand_landmarks:
                data = list(results.left_hand_landmarks.landmark)
                for index, value in enumerate(data):
                    left_hand_csv = (
                        left_hand_csv
                        + f"{index},"
                        + f"{value.x},"
                        + f"{value.y},"
                        + f"{value.z} \n"
                    )
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            while True:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )
                mp_drawing.draw_landmarks(
                    image,
                    results.left_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )

                mp_drawing.draw_landmarks(
                    image,
                    results.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style(),
                )

                mp_drawing.draw_axis(image, np.eye(3), np.zeros(3))
                image.flags.writeable = True
                cv2.imshow("MediaPipe Holistic", image)
                if cv2.waitKey(1) == ord("q"):
                    break

    file = open(f"./gesture/base_poses_hf/{pose_name}.csv", "w")
    file.write(pose_csv)
    file.close()

    file = open(f"./gesture/base_poses_hf/{left_name}.csv", "w")
    file.write(left_hand_csv)
    file.close()

    file = open(f"./gesture/base_poses_hf/{rigth_name}.csv", "w")
    file.write(right_hand_csv)
    file.close()


if __name__ == "__main__":
    if execute_parallel:
        with Pool() as p:
            p.map(transcribe_word, images)
            # This seems to introduce a memory leak, still not a problem on my
            # machine but can be a problem for others. I recommend using parallel
            # execution only if your system has 32GB of RAM or more.
    else:
        for word in images:
            print(word)
            transcribe_word(word)
