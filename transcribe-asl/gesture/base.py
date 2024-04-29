from pyscript import window
# import pandas as pd
import numpy as np
# from typing import Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

class Gesture:

    def __init__(
        self,
        base_gestures: dict[str, dict[str, np.array]] = None,
    ):
        """
        Initialize the Gesture object.

        Parameters
        ----------
        base_gestures: dict[str, dict[str, np.array]]
            A dictionary containing the base gestures.
            The keys are the names of the gestures.
            The values are dictionaries containing the base points of the right, left, and body gestures.

        Examples
        --------
        base_gestures["one"]["right"] = np.array([[x1, y1, z1], [x2, y2, z2], ...])
        base_gestures["one"]["left"] = np.array([[x1, y1, z1], [x2, y2, z2], ...])
        base_gestures["one"]["body"] = np.array([[x1, y1, z1], [x2, y2, z2], ...])
        """
        # Define the gestures.
        self.gestures: np.array[str] = np.array(
            [
                "one",
                "one_inv",
                "two",
                "two_inv",
                "three",
                "three_inv",
                "four",
                "four_inv",
                "five",
                "five_inv",
                "six",
                "seven",
                "eight",
                "nine",
                "ten_1",
                "ten_2",
                "ten_3",
                "closed_fist",
                "left_thumb_right",
                "zero",
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
                "i_down",
                "i_flipped",
                "K",
                "L",
                "M",
                "N",
                "O",
                "P",
                "Q",
                "R",
                "S",
                "T",
                "U",
                "V",
                "W",
                "X",
                "Y",
            ]
            # [
            #     "two",
            #     "P",
            #     "seven",
            # ]
        )
        # Define the gestures with movements.
        self.gestures_mov: dict[str, list[str]] = {
            "ten": ["ten_1", "ten_2", "ten_3"],
            "eleven": ["one", "closed_fist", "one"],
            "twelve": ["two", "closed_fist", "two"],
            "thirteen": ["three", "left_thumb_right", "three"],
            "fourteen": ["four", "closed_fist", "four"],
            "fifteen": ["five", "left_thumb_right", "five"],
            "sixteen": ["closed_fist", "six"],
            "seventeen": ["left_thumb_right", "seven"],
            "eighteen": ["left_thumb_right", "eight"],
            "nineteen": ["left_thumb_right", "nine"],
            "J": ["I", "i_down", "i_flipped"],
        }
        if base_gestures is None:
            self.base_gestures: dict[str, dict[str, np.array]] = (
                Gesture.get_base_gestures(self.gestures)
            )
        else:
            self.base_gestures = base_gestures

        self.past_gestures = []
        self.check_point: dict[str, int] = {gesture: 0 for gesture in self.gestures_mov}
        self.check_point_time = datetime.now() - timedelta(seconds=60)
    # Needed for the web version... Really just sets things to the window object.
    def classify(
        self,
        obj_in
    ) -> tuple[str, list[str]]:
        right_obj = json.loads(obj_in.right)
        left_obj = json.loads(obj_in.left)
        body_obj = json.loads(obj_in.body)

        right = np.array(right_obj)
        left = np.array(left_obj)
        body = np.array(body_obj)
        
        return self.predict(right, left, body)
    
    def predict(
        self,
        obj_in
    ) -> tuple[str, list[str]]:
        top_most = 3
        """
        Predict the gesture.

        Parameters
        ----------
        right: np.array
            The points of the right hand.
        left: np.array
            The points of the left hand.
        body: np.array
            The points of the body.
        top_most: int
            The number of top most closest gestures to return.

        Returns
        -------
        static_gestures: list[str]
            The top most static gestures.
        mov_gesture: list[str]
            The movement gesture.
        static_gestures_confidence: dict[str, float]
            The confidence of the static gestures.
        """
        
        right_obj = json.loads(obj_in.right)
        left_obj = json.loads(obj_in.left)
        body_obj = json.loads(obj_in.body)

        right = np.array(right_obj)
        left = np.array(left_obj)
        body = np.array(body_obj)
        # Reset the check points.
        self._reset_check_points(wait_seconds=5)
        # For The pose one, all we need is the right hand.
        static_gesture: str = "Nothing recognized"

        if left is None and right is not None:
            static_gesture = "No left hand gesture"

        static_gestures: list[str] = [static_gesture]
        static_gestures_confidence: dict[str, float] = {static_gesture: 0}

        # It's a cascade of poses.... First start with one then it drills down into the other ones.
        if right is not None:
            # Compare incoming points with the static gestures.
            errors_gesture: dict[str, float] = {
                gesture: self._compare_hand(
                    self.base_gestures[gesture]["right_hand"], right
                )
                for gesture in self.base_gestures
            }
            static_gestures: list[str] = sorted(errors_gesture, key=errors_gesture.get)[
                :top_most
            ]  # The identified static gesture is the one with the smallest error.
            # Don't need this in code but it helps debugging.
            static_gesture = static_gestures[0]
            self.past_gestures.append(static_gestures)
            # Update the check points.
            self._update_check_points(static_gesture)
            # Calculate the confidence of the top most gestures.
            static_gestures_confidence: dict[str, float] = self._get_confidence(
                static_gestures, errors_gesture
            )
        # Check if there is a movement in the buffer of identified static gestures.
        mov_gestures: list[str] = self._identify_gestures_movement()
        
        # This may break with local. Sorry...
        window.static_gesture = static_gesture
        window.movement_gesture = mov_gestures
        window.static_gestures_confidence = static_gestures_confidence
        
        print(static_gestures_confidence)
        print(mov_gestures)
        print(static_gesture)
        # Keeping this light for now b/c of frontend.
        return (static_gestures, mov_gestures, static_gestures_confidence)

    def _is_pointed_finger(self, right: np.array) -> bool:
        """
        Check if the hand is in the pointed finger pose.

        Returns
        -------
        is_pointed_finger: bool
            A bool indicating if the hand is in the pointed finger pose.
        """
        # df = pd.DataFrame(right, columns=["x", "y", "z"])  # isn't this x, y, z? YES!
        # df = pd.DataFrame(right, columns=["x", "y", "z"])  # isn't this x, y, z? YES!

        # print(df)
        # index_finger_height = df["y"].iloc[8]
        # max_limb_height = df.nlargest(1, "y")["y"].iloc[0]
        # print(df.nlargest(1, "y"))
        # print(index_finger_height)
        # print(df)
        # index_finger_height = df["y"].iloc[8]
        # max_limb_height = df.nlargest(1, "y")["y"].iloc[0]
        # print(df.nlargest(1, "y"))
        # print(index_finger_height)

        """
        Note: This works pretty consistently for the pointed finger pose.
        But it's important to undestand what's the orientation of the camera. 
        """

        if index_finger_height == max_limb_height:
            return True
        else:
            return False

    def _compare_hand(self, base_points: np.array, incoming_points: np.array) -> float:
        """
        Compare the base points of the hand with the incoming points of the hand.

        Parameters
        ----------
        base_points: np.array
            The base points of the hand.
        incoming_points: np.array
            The incoming points of the hand.

        Returns
        -------
        error: float
            The error between the base points and the incoming points.
        """
        # Load the base points in the hand frame of reference.
        # For some reason the copy function was failing... Not sure if we need to copy.
        base_points_zzero: np.array = base_points
        # base_points_zzero[:, 2] = 0
        base_points_in_hand_frame: np.array = to_hand_frame(base_points_zzero)
        # get the incoming poitns in the hand frame of reference.
        incoming_points_zzero: np.array = incoming_points
        # incoming_points_zzero[:, 2] = 0
        incoming_points_in_hand_frame: np.array = to_hand_frame(incoming_points_zzero)
        # Mean squared error of distance of points.
        error_points_distance = mean_squared_error(
            base_points_in_hand_frame,  # [:, :2],
            incoming_points_in_hand_frame,  # [:, :2]
        )
        # Get the angle indicating of the base and incoming points.
        angle_hand_inc = angle_hand(incoming_points)
        angle_hand_base = angle_hand(base_points)
        # Mean squared error of the angle of the hand.
        error_rotation = mean_absolute_error(angle_hand_base, angle_hand_inc) / (
            8 * np.pi
        )
        # 8 * np.pi is the best tested scaling factor
        error = error_points_distance + error_rotation
        return error

    def _compare_body(
        self, body_base_points: np.array, body_incoming_points: np.array
    ) -> float:
        """
        Compare the base points of the body with the incoming points of the body.

        Parameters
        ----------
        body_base_points: np.array
            The base points of the body.
        body_incoming_points: np.array
            The incoming points of the body.

        Returns
        -------
        error: float
            The error between the base points and the incoming points.
        """
        pass

    def _compare_both_hands(
        self,
        right_base_points: np.array,
        left_base_points: np.array,
        right_incoming_points: np.array,
        left_incoming_points: np.array,
    ) -> float:
        """
        Compare the base points of both hands with the incoming points of both hands.

        Parameters
        ----------
        right_base_points: np.array
            The base points of the right hand.
        left_base_points: np.array
            The base points of the left hand.
        right_incoming_points: np.array
            The incoming points of the right hand.
        left_incoming_points: np.array
            The incoming points of the left hand.

        Returns
        -------
        error: float
            The error between the base points and the incoming points.
        """
        # Get the error of the right hand.
        error_right: float = self._compare_hand(
            right_base_points, right_incoming_points
        )
        # Get the error of the left hand.
        error_left: float = self._compare_hand(left_base_points, left_incoming_points)
        # match the points of both hands.
        return (error_right + error_left) / 2

    def _compare_hand_check_points(
        self, base_points: np.array, incoming_points: np.array
    ) -> float:
        """
        Compare the base points of the hand with the incoming points of the hand, but only if check point is zero.

        Parameters
        ----------
        base_points: np.array
            The base points of the hand.
        incoming_points: np.array
            The incoming points of the hand.

        Returns
        -------
        error: float
            The error between the base points and the incoming points.

        Note
        ----
        This function is used to compare the incoming points with the base points of the hand only if the check point
        is zero. If the check point is not zero, the function returns a big error.
        """
        if self.check_point == 0:
            return self._compare_hand(base_points[:, :, 0], incoming_points)
        else:
            return 1e3  # big error

    def _compare_hand_movement(
        self, base_points: np.array, incoming_points: np.array
    ) -> float:
        """
        Compare the base points of the hand with the incoming points of the hand in terms of movement.

        Parameters
        ----------
        base_points: np.array
            The base points of the hand.
        incoming_points: np.array
            The incoming points of the hand.

        Returns
        -------
        error: float
            The error between the base points and the incoming points.
        """
        # 1
        """
        There is another possible approach, which is to average every point in the incoming points
        and compare it with the base points average of the gesture. This should be simpler and more
        but it's not clear if it's more accurate.
        """
        # 2
        """
        The proposed approach is to compare the incoming points with check points.
        There are n check points. The incoming points are compared with the first check point.
        If it passes, in the next frame it's compared with the second check point, and so on.

        Possible problems:
        1 - The next frame doesn't yet contain the next check point because the movement is too slow.
        2 - The next frame doesn't contain the next check point because the movement is too fast.
        3 - If a check point is missed, how to resume the comparison?
        4 - How to determine the number of check points?
        5 - What about the speed of the movement, does it matter?

        Assumptions:
        5 - The speed of the movement is not important.
        4 - The number of check points is determined by the user, there can be as many as desired.
        3 - As soon as the first check point is captured, a clock starts. 
            If the next check point is not captured within a certain time, it resets.
        2 - See 3.
        1 - See 3.
        """
        # Lets try the second approach first.

        # The first step is to compare the incoming points with the one from the check point.
        if self.check_point < base_points.shape[2]:
            error = self._compare_hand(
                to_hand_frame(base_points[:, :, self.check_point]),
                to_hand_frame(incoming_points),
            )
            # Note: Base_points_in_hand_frame is a 3D array. The third dimension is the number of check points.
            if error < 1e-2:  # this is bad
                if self.check_point == 0:
                    self.check_point_time = datetime.now()
                self.check_point += 1
            return error
        else:
            return self._compare_hand(
                to_hand_frame(base_points[:, :, base_points.shape[2] - 1]),
                to_hand_frame(incoming_points),
            )

    def _update_check_points(self, gesture: str):
        """
        Update the check points.

        Parameters
        ----------
        gesture: str
            The gesture to update the check points.
        """
        for gesture_mov in self.gestures_mov:
            if (
                self.check_point[gesture_mov] < len(self.gestures_mov[gesture_mov])
                and gesture
                == self.gestures_mov[gesture_mov][self.check_point[gesture_mov]]
            ):
                if np.sum([self.check_point[key] for key in self.check_point]) == 0:
                    self.check_point_time = datetime.now()  # ?
                self.check_point[gesture_mov] += 1

    def _reset_check_points(self, wait_seconds: int = 5):
        """
        Reset the check points.
        """
        # Reset the check point if it's been too long.
        if datetime.now() - self.check_point_time > timedelta(seconds=wait_seconds):
            self.check_point = {gesture: 0 for gesture in self.gestures_mov}
            self.check_point_time = datetime.now() - timedelta(seconds=60)
            self.past_gestures = []

    def _identify_gestures_movement(self) -> str:
        """
        Identify if there is a gesture in the buffer of identified static gestures.

        Returns
        -------
        gesture_movement: str
            The identified gesture.
        """
        identified_gestures: list[str] = []
        for gesture_mov in self.gestures_mov:
            if self.check_point[gesture_mov] == len(self.gestures_mov[gesture_mov]):
                identified_gestures.append(gesture_mov)
        return identified_gestures

    def _get_confidence(
        self, static_gestures: list[str], errors_gesture: dict[str, float]
    ) -> dict[str, float]:
        """
        Calculate the confidence of the top most gestures.

        Parameters
        ----------
        static_gestures: list[str]
            The top most static gestures.
        errors_gesture: dict[str, float]
            The errors of the gestures.

        Returns
        -------
        confidence_gesture: dict[str, float]
            The confidence of the gestures.
        """
        errors = np.array([errors_gesture[gesture] for gesture in static_gestures])
        """
        To create the confidence, the error is normalized by the maximum possible error.
        the idea is that if the error is zero, the confidence is 1, and if the error is the maximum possible error,
        the confidence is zero. A meaningfull maximum possible error should is the error A and five.
        """
        max_possible_error: float = self._compare_hand(
            self.base_gestures["A"]["right_hand"],
            self.base_gestures["five"]["right_hand"],
        )
        # NOTE to self: max_possible error is not actually the max possible error,
        # only a good approximation.
        # since sometimes the confidence is smaller than zero, only possible if 
        # the error is larger than the max_possible_error.
        confidences: np.array = 1 - errors / max_possible_error
        for i, confidence in enumerate(confidences):
            if confidence < 0:
                confidences[i] = 0
        confidence_gesture: dict[str, float] = {
            gesture: confidence
            for gesture, confidence in zip(static_gestures, confidences)
        }
        return confidence_gesture

    @staticmethod
    def get_base_gestures(gestures: list[str]) -> dict[str, dict[str, np.array]]:
        """
        Get the base gestures.

        Returns
        -------
        base_gestures: dict[str,dict[str,np.array]]
            A dictionary containing the base gestures.
        """
        # Define the base gestures path
        base_path: str = "./"
        # Load the base gestures from the database.
        base_gestures: dict[str, dict[str, np.array]] = {}
        for gesture in gestures:
            base_gestures[gesture] = {
                "right_hand": load_base_gesture(
                    f"{base_path}/{gesture}_Transcription_Right_Hand.csv"
                ),
                "left_hand": load_base_gesture(
                    f"{base_path}/{gesture}_Transcription_Left_Hand.csv"
                ),
                "pose": load_base_gesture(
                    f"{base_path}/{gesture}_Transcription_Pose.csv"
                ),
            }
        return base_gestures


def concat_or_none(array: list[np.array]) -> np.array:
    """
    Concatenate a list of arrays or return None if the list is empty.

    Parameters
    ----------
    array: list[np.array]
        A list of arrays.

    Returns
    -------
    concatenated_array: Optional[np.array]
        The concatenated array if the list is not empty, otherwise None.
    """
    if not (np.array(array) == None).all():  # noqa
        return np.concatenate(array, axis=2)
    else:
        return None


def load_base_gesture(path: str) -> np.array:
    """
    Load the base gesture from a file.

    Parameters
    ----------
    path: str
        The path to the file.

    Returns
    -------
    base_gesture: Optional[np.array]
        The base gesture if exists.
    """
    base_gesture = np.genfromtxt(path, delimiter=",")
    if len(base_gesture.shape) > 1:  # Check if the base gesture is not empty.
        return base_gesture[1:, 1:]
    else:
        return None


def mean_squared_error(y_true: np.array, y_pred: np.array) -> float:
    """
    Compute the mean squared error.

    Parameters
    ----------
    y_true: np.array
        The true values.
    y_pred: np.array
        The predicted values.

    Returns
    -------
    mse: float
        The mean squared error.
    """
    return np.square(y_true - y_pred).mean()


def mean_absolute_error(y_true: np.array, y_pred: np.array) -> float:
    """
    Compute the mean absolute error.

    Parameters
    ----------
    y_true: np.array
        The true values.
    y_pred: np.array
        The predicted values.

    Returns
    -------
    mae: float
        The mean absolute error.
    """
    return np.abs(y_true - y_pred).mean()


# auxillary functions (Not sure they should be here or not but I think it deserves its own file)
def hand_frame_of_reference(coordinates: np.array) -> np.array:
    """Get the hand frame of reference.

    Parameters
    ----------
    coordinates: np.array
        A 2D array containing the coordinates of the points.
        Coordinates are expected to be sorted according to their index.

    Returns
    -------
    hand_frame: np.array
        A 2D array containing the base vectors of the hand frame of reference in global coordinates.
    """
    hand_frame = np.zeros((3, 3))
    # the plane passes through the points 0, 5, and 17
    points_in_plane = coordinates[[0, 5, 17]].astype(float)
    # The z vector is the cross product of the vectors formed by the points 0-5 and 0-17
    # It's a vector normal to the plane.
    z_vec = np.cross(
        points_in_plane[1] - points_in_plane[0], points_in_plane[2] - points_in_plane[0]
    )
    # The z base vector is the normalized z vector
    hand_frame[2] = z_vec / np.linalg.norm(z_vec)
    # The y vector is the vector formed by the points 0 and 5
    y_vec = points_in_plane[2] - points_in_plane[0]
    # The y base vector is the normalized y vector
    hand_frame[1] = y_vec / np.linalg.norm(y_vec)
    # The x base vector is the cross product of the y and z base vectors
    hand_frame[0] = np.cross(hand_frame[2], hand_frame[1])
    return hand_frame.T


def to_hand_frame(coordinates: np.array, norm: bool = True) -> np.array:
    """Rotate and translates the coordinates to the hand frame of reference.

    Parameters
    ----------
    coordinates: np.array
        A 2D array containing the coordinates of the points to rotate.
    norm: bool
        A bool indicating if the coordinates should be normalized.

    Returns
    -------
    coordinates_hand_frame: np.array
        A 2D array containing the coordinates of the points in the hand frame of reference.
    """
    coordinates = coordinates.astype(float)
    # The hand frame of reference is obtained by the hand_frame_of_reference function.
    hand_frame = hand_frame_of_reference(coordinates)
    # The rotation matrix is the transpose of the hand frame of reference.
    rotation_matrix = hand_frame.T
    # The coordinates in the hand frame of reference are obtained by multiplying the rotation matrix by the coordinates.
    coordinates_hand_frame = np.zeros_like(coordinates)
    for i in range(coordinates.shape[0]):
        coordinates_hand_frame[i] = np.dot(
            rotation_matrix, coordinates[i] - coordinates[0]
        )
    # for i in range(coordinates.shape[0]):
    #     coordinates_hand_frame[i] = coordinates[i] - coordinates[0]
    if norm:
        # The coordinates are normalized by dividing them by the maximum absolute value of the coordinates.
        coordinates_hand_frame = coordinates_hand_frame / np.abs(
            coordinates_hand_frame
        ).max(axis=0)
    return coordinates_hand_frame


def euler_angles_from_rotation_matrix(rotation_matrix: np.array) -> np.array:
    """Get the Euler angles from the rotation matrix.

    Parameters
    ----------
    rotation_matrix: np.array
        A 2D array containing the rotation matrix.

    Returns
    -------
    euler_angles: np.array
        A 1D array containing the Euler angles.
    """
    # The Euler angles are obtained by the arctangent of the ratio of the elements of the rotation matrix.
    # The rotation matrix is assumed to be in the ZYX order.
    euler_angles = np.zeros(3)
    euler_angles[0] = np.arctan2(
        rotation_matrix[1, 2], rotation_matrix[2, 2]
    )  # phi_x = arctan2(r23, r33)
    euler_angles[1] = -np.arcsin(rotation_matrix[0, 2])  # theta_y = -arcsin(r13)
    euler_angles[2] = np.arctan2(
        rotation_matrix[0, 1], rotation_matrix[0, 0]
    )  # psi_z = arctan2(r12, r11)
    for i, euler_angle in enumerate(euler_angles):
        if euler_angle < 0:
            euler_angles[i] += 2 * np.pi

    return euler_angles


def angle_hand(coordinates: np.array) -> float:
    """Get the angle of the hand.

    Parameters
    ----------
    coordinates: np.array
        A 2D array containing the coordinates of the points.

    Returns
    -------
    angle: float
        The angle of the hand.
    """
    # The angle of the hand is the angle between the x and y base vectors of the hand frame of reference.
    hand_frame = hand_frame_of_reference(coordinates.astype(float))
    angle = np.arctan2(hand_frame[1, 1], hand_frame[1, 0])
    if angle < 0:
        angle += 2 * np.pi
    return angle


def match_position_points(base_points: np.array, points: np.array) -> np.array:
    """Match the position of the points to the base points.

    Parameters
    ----------
    base_points: np.array
        A 2D array containing the base points in the hand frame of reference.
    points: np.array
        A 2D array containing the points to match in the hand frame of reference.

    Returns
    -------
    points_matched: bool
        A bool indicating if the points were matched.

    Note
    ----
       For this to work properly, the points should be in the hand frame of reference.
    """

    return np.allclose(base_points, points, atol=9e-2)


def sigmoid(x):
    """
    The sigmoid function.

    Parameters
    ----------
    x: float
        The input.

    Returns
    -------
    y: float
        The output.
    """
    return 2 / (1 + np.exp(-x)) - 1


# @dataclass
# class Output:
#     """
#     The output of the model.

#     Attributes
#     ----------
#     static_gestures: list[str]
#         The top most static gestures.
#     movement_gestures: list[str]
#         The movement gesture.
#     static_gestures_confidence: dict[str, float]
#         The confidence of the static gestures.
#     """

#     static_gestures: list[str]
#     movement_gestures: list[str]
#     static_gestures_confidence: dict[str, float]
