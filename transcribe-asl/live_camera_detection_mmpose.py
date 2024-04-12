import cv2
import mediapipe as mp
import time
from gesture.base import Gesture, to_hand_frame
import numpy as np
from mmpose.apis import MMPoseInferencer, inference_topdown, init_model
from mmpose.registry import VISUALIZERS
from mmpose.apis.inferencers.utils import default_det_models, get_model_aliases

import os.path as osp

from mmengine.config.utils import MODULE2PACKAGE
from mmengine.utils import get_installed_path

# fix base_dense_head as https://github.com/open-mmlab/mmdetection/issues/11063
# I changed my own file in venv since its easier

print(get_model_aliases('mmdet'))

mmpose_path = get_installed_path(MODULE2PACKAGE['mmpose'])
mmdet_path = get_installed_path(MODULE2PACKAGE['mmdet'])

# 
object_type = "hand"
det_info = default_det_models[object_type]
det_info['cat_ids'] = tuple(range(10))
# Printing the bounding box is possible to see that the detection is fine and the problem is the had
# Get model values at https://github.com/open-mmlab/mmdetection/tree/main/configs
# det_info = dict(
#     model=osp.join(mmdet_path, ".mim", "configs/ssd/ssdlite_mobilenetv2-scratch_8xb24-600e_coco.py"),
#     weights='https://download.openmmlab.com/mmdetection/v2.0/ssd/ssdlite_mobilenetv2_scratch_600e_coco/'
#     'ssdlite_mobilenetv2_scratch_600e_coco_20210629_110627-974d9307.pth',
#     cat_ids=tuple(0,)
# )
# det_info = dict(
#     model=osp.join(mmdet_path, ".mim", "configs/ssd/ssdlite_mobilenetv2-scratch_8xb24-600e_coco.py"),
#     weights='https://github.com/open-mmlab/mmdetection/blob/main/configs/rtmdet/rtmdet_tiny_8xb32-300e_coco.py',
#     cat_ids=(4, )
# )
det_model, det_weights, det_cat_ids = (
    det_info["model"],
    det_info["weights"],
    det_info["cat_ids"],
)
inferencer = MMPoseInferencer("hand3d", det_model=det_model, det_weights=det_weights, det_cat_ids=det_cat_ids)
# inferencer = MMPoseInferencer("hand3d", det_model='ssdlite')
# inferencer = MMPoseInferencer("hand3d")
# inferencer = MMPoseInferencer("hand")

# model = init_model("internet_res50_4xb16-20e_interhand3d-256x256.py", "hand3d")
# inferencer = inference_topdown("hand3d", det_model="ssdlite_mobilenetv2")


def main():

    g = Gesture()  # Load outside to prevent reloading base gestures from disk

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_holistic = mp.solutions.holistic

    # access webcam
    cap = cv2.VideoCapture(0)
    # address = "http://192.168.15.35:8080/video"
    # cap.open(address)
    # inferencer = MMPoseInferencer("hand")
    while True:
        # pull frame
        start = time.time()
        ret, frame = cap.read()
        frame = cv2.resize(frame, (1080, 720))  # In the end makes everything faster
        # mirror frame
        # frame = cv2.flip(frame, 1)
        # display frame
        if cv2.waitKey(1) == ord("q"):
            break

        # frame.flags.writeable = True

        # make prediction
        result = next(inferencer(frame))
        # mp_drawing.draw_axis(
        #     frame,
        #     np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]]),
        #     np.array([0.089, -0.089, 0]),
        # )

        # This is important, it draws the axis of the camera.

        end = time.time()

        fps = 1 / (end - start)
        # # TODO: Insert pose_recognized code here... Import module and run command.
        right_hand_data = None
        pose_data = None
        left_hand_data = None
        # if results.right_hand_landmarks:
        #     # TODO: Move this repetitive code into a function or module somewhere...
        #     right_hand_raw = list(results.right_hand_landmarks.landmark)
        right_hand_raw = np.array(result["predictions"][0][0]["keypoints"])  # [:,:2]
        right_hand_data = right_hand_raw[:21]
        draw_hand_from_kps(frame, right_hand_data)
        # if results.pose_landmarks:
        #     pose_raw = list(results.pose_landmarks.landmark)
        #     pose_data = np.array(
        #         [[value.x, value.y, value.z] for value in pose_raw]
        #     )
        # if results.left_hand_landmarks:
        #     left_hand_raw = list(results.left_hand_landmarks.landmark)
        #     left_hand_data = np.array(
        #         [[value.x, value.y, value.z] for value in left_hand_raw]
        #     )
        # Draw bounding box
        bboxs = result["predictions"][0][0]["bbox"]
        for bbox in bboxs:
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3]),), (0, 255, 0), 2)

        recognition_output_static, recognition_output_mov = g.predict(
            right_hand_data, left_hand_data, pose_data
        )

        # draw_rotated_left_hand(frame, left_hand_data)

        draw_rotated_right_hand(frame, right_hand_data)

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

        cv2.putText(
            frame,
            f"FPS: {int(fps)}   Static: {recognition_output_static}",
            (20, 70),
            cv2.FONT_HERSHEY_PLAIN,
            3,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            f"Movement: {recognition_output_mov}",
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
    scale=1 / 3,
):
    """
    Draw the left hand landmarks in the top left corner of the frame.
    """
    # Draw left hand smaller in corner

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
    draw_hand_from_kps(
        frame,
        left_hand_data_small[:, :2],
    )


def draw_rotated_right_hand(
    frame,
    right_hand_data,
    scale=1 / 3,
):
    """
    Draw the right hand landmarks in the top right corner of the frame.
    """
    # Draw right hand smaller in corner
    right_hand_data_frame = to_hand_frame(right_hand_data, norm=False).dot(
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
    )
    if np.isnan(right_hand_data_frame).any():
        right_hand_data_frame = right_hand_data
    right_hand_data_small = right_hand_data_frame * scale
    right_hand_data_small[:, 0] = (
        right_hand_data_small[:, 0] - right_hand_data_small[:, 0].max() + 1080 - 20
    )
    right_hand_data_small[:, 1] = (
        right_hand_data_small[:, 1] - right_hand_data_small[:, 1].max() + 720 - 20
    )
    # right_hand_data_small[:, 2] = right_hand_data_small[:, 2] - right_hand_data_small[:, 2].min()

    draw_hand_from_kps(
        frame,
        right_hand_data_small,
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


def draw_hand_from_kps(img, kps):
    """
    Draw hand keypoints on the given image.

    Parameters:
        img (ndarray): The input image.
        kps (list): List of hand keypoints.

    Returns:
        ndarray: The image with hand keypoints drawn.

    Keypoints Format:
        Each keypoint is represented as a tuple (x, y), where x and y are the coordinates of the keypoint.

    Hand Connections:
        The hand connections define the order in which keypoints are connected to form the hand skeleton.
        The connections are defined as a list of lists, where each inner list represents a connection between keypoints.
        For example, [0, 1, 2, 3, 4] represents a connection between keypoints 0 and 1, 1 and 2, 2 and 3, and 3 and 4.

    Example:
        img = cv2.imread('image.jpg')
        kps = [(100, 200), (150, 250), ...]
        img_with_keypoints = draw_hand_from_kps(img, kps)
    """
    hand_connections = [
        [0, 1, 2, 3, 4],
        [0, 5, 6, 7, 8],
        [0, 9, 10, 11, 12],
        [0, 13, 14, 15, 16],
        [0, 17, 18, 19, 20],
    ]
    for kp in kps:
        x, y, z = kp
        cv2.circle(img, (int(x), int(y)), 5, (255, 0, 0), -1)
    for connections in hand_connections:
        for i in range(len(connections) - 1):
            x1, y1, z1 = kps[connections[i]]
            x2, y2, z2 = kps[connections[i + 1]]
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    return img


if __name__ == "__main__":
    main()
