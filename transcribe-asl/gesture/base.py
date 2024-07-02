# from pyscript import window

# import pandas as pd
import numpy as np
from scipy.stats import pmean

# from typing import Optional
from datetime import datetime

# from dataclasses import dataclass
import json
from collections import deque


class Gesture:

    def __init__(
        self,
        base_gestures: dict[str, dict[str, np.array]] = None,
        base_acc_gestures: dict[str, dict[str, np.array]] = None,
    ):
        """
        Initialize the Gesture object.

        Parameters
        ----------
        base_gestures: dict[str, dict[str, np.array]]
            A dictionary containing the base gestures.
            The keys are the names of the gestures.
            The values are dictionaries containing the base points of the right, left, and body gestures.
        mmpose: bool
            A bool indicating if the model is using the mmpose library.

        Examples
        --------
        base_gestures["one"]["right"] = np.array([[x1, y1, z1], [x2, y2, z2], ...])
        base_gestures["one"]["left"] = np.array([[x1, y1, z1], [x2, y2, z2], ...])
        base_gestures["one"]["body"] = np.array([[x1, y1, z1], [x2, y2, z2], ...])
        """
        # Define the gestures.
        self.gestures: np.array[str] = Gesture.get_gestures_names()
        self.gestures_mov_names: np.array[str] = Gesture.get_gestures_names_mov()
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
        if base_acc_gestures is None:
            self.base_acc_gestures: dict[str, dict[str, np.array]] = (
                Gesture.get_base_gestures(self.gestures_mov_names)
            )
        else:
            self.base_acc_gestures = base_acc_gestures

        self.past_gestures: deque[str] = deque(maxlen=120)
        self.buffer_hand: deque[np.array] = deque(maxlen=120)
        self.check_point: dict[str, int] = {gesture: 0 for gesture in self.gestures_mov}
        self.identified_mov_gestures: deque[str] = deque(maxlen=3)
        self.mmpose: bool = False

    def set_gestures(self, gestures: np.array) -> bool:
        self.gestures = gestures
        self.base_gestures: dict[str, dict[str, np.array]] = Gesture.get_base_gestures(
            self.gestures
        )
        return True

    # Needed for the web version... Really just sets things to the window object.
    def classify(self, obj_in) -> tuple[str, list[str]]:
        right_obj = json.loads(obj_in.right)
        left_obj = json.loads(obj_in.left)
        body_obj = json.loads(obj_in.body)

        right = np.array(right_obj)
        left = np.array(left_obj)
        body = np.array(body_obj)

        return self.predict(right, left, body)

    def predict(self, obj_in) -> tuple[str, list[str]]:
        top_most = 3
        """
        Predict the gesture.

        A _predict wrapper function to be used on the frontend.

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

        static_gestures, mov_gestures, static_gestures_confidence = self._predict(
            right, left, body, top_most
        )
        static_gestures_confidence = []
        # This may break with local. Sorry...
        window.static_gesture = static_gestures[0]
        window.movement_gesture = mov_gestures
        # window.static_gestures_confidence = static_gestures_confidence
        return (static_gestures, mov_gestures, static_gestures_confidence)

    def _predict(
        self,
        right: np.array = None,
        left: np.array = None,
        body: np.array = None,
        top_most: int = 3,
    ) -> tuple[list[str], list[str], dict[str, float]]:
        """
        Predict the gesture.

        The main function to predict the gesture.

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
        # Reset the check points.
        self._reset_check_points()
        # CHECKPOINTS ARE RESETED AFTER EVERY FRAME.
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
            self.buffer_hand.append(right)
            self.past_gestures.append(static_gestures)
            # Update the check points.
            # self._update_check_points(static_gesture)
            # Calculate the confidence of the top most gestures.
            # TODO: reimplement this.
            static_gestures_confidence: dict[str, float] = self._get_confidence(
                static_gestures, errors_gesture
            )
        # Check if there is a movement in the buffer of identified static gestures.
        # mov_gestures: list[str] = self._identify_gestures_movement()
        mov_gestures: list[str] = self._iden_gest_mov_acc(top_most)
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

        # index_finger_height = df["y"].iloc[8]
        # max_limb_height = df.nlargest(1, "y")["y"].iloc[0]

        # index_finger_height = df["y"].iloc[8]
        # max_limb_height = df.nlargest(1, "y")["y"].iloc[0]

    #     """
    #     Note: This works pretty consistently for the pointed finger pose.
    #     But it's important to undestand what's the orientation of the camera.
    #     """

    # if index_finger_height == max_limb_height:
    #     return True
    # else:
    #     return False

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
        base_points_in_hand_frame: np.array = to_hand_frame(base_points)
        # Load the incoming points in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(incoming_points)
        if self.mmpose:
            base_points_in_hand_frame = base_points_in_hand_frame[:, :2]
            incoming_points_in_hand_frame = incoming_points_in_hand_frame[:, :2]
        # # Mean squared error of distance of points.
        # error_points_distance = mean_squared_error(
        #     base_points_in_hand_frame,  # [:, :2],
        #     incoming_points_in_hand_frame,  # [:, :2]
        # )
        # # Get the angle indicating of the base and incoming points.
        angle_hand_inc = angle_hand(incoming_points)
        # print(angle_hand_inc)
        angle_hand_base = angle_hand(base_points)
        # # Mean squared error of the angle of the hand.
        error_rotation = mean_absolute_error(angle_hand_base, angle_hand_inc) / (
            8 * np.pi
        )
        # print(error_rotation)
        # # 8 * np.pi is the best tested scaling factor

        error_points_distance = cosine_similarity(
            base_points_in_hand_frame,
            incoming_points_in_hand_frame,
            flatten=True,
        )
        # error = 1-cosine_similarity(
        #     base_points_zzero.flatten(), incoming_points_zzero.flatten()
        # )
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
        3 - All identified poses are added to a buffer of 120 gestures, i.e., 2 s @ 60fps.
        2 - After a new gesture is identified, the buffer is analyzed to see if there is a movement.
        which prevents having to wait for the clock to reset the buffer.
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
                self.check_point[gesture_mov] += 1

    def _reset_check_points(self):
        """
        Reset the check points.
        """
        # Reset the check points.
        self.check_point = {gesture: 0 for gesture in self.gestures_mov}

    def _identify_gestures_movement(self) -> None:
        """
        Identify if there is a gesture in the buffer of identified static gestures.

        Note: Updates the identified gestures buffer.
        """
        for gesture_mov in self.gestures_mov:
            if self.check_point[gesture_mov] == len(self.gestures_mov[gesture_mov]):
                if gesture_mov not in self.identified_mov_gestures:
                    self.identified_mov_gestures.appendleft(gesture_mov)

    def _iden_gest_mov_acc(self, top_most: int) -> tuple[list[str], list[float]]:
        """
        Identify if there is a gesture in the buffer of hand positions.

        This method uses the accumulation approach to identify the gesture.
        The idea is to accumulate the positions of the interest points in
        the hand into a single modified hand, that is then used for compari-
        son with the base gestures, created using the same approach.

        This approach is based on the ideas of the paper [1].

        Parameters
        ----------
        top_most: int
            The number of top most closest gestures to return.

        Returns
        -------
        gesture_movement: list[str]
            The top identified gesture movements.
        gesture_movement_confidence: list[float]
            The confidence of the identified gesture movements.

        References
        ----------
        [1] - Caliwag, Angela C., et al. "Movement-in-a-video detection scheme
        for sign language gesture recognition using neural network." Applied
        Sciences 12.20 (2022): 10542.
        """
        # Get the accumulated hand.
        accumulated_hand = self._accumulate_hand()
        # Compare the accumulated hand with the base gestures.
        errors_gesture: dict[str, float] = {
            gesture: self._compare_hand(
                self.base_acc_gestures[gesture]["right_hand"], accumulated_hand
            )
            for gesture in self.base_acc_gestures
        }
        # Get the top most closest gestures.
        mov_gestures: list[str] = sorted(errors_gesture, key=errors_gesture.get)[
            :top_most
        ]
        self.identified_mov_gestures.appendleft(mov_gestures[0])
        # Calculate the confidence of the top most gestures.
        mov_gestures_confidence: dict[str, float] = self._get_confidence(
            mov_gestures, errors_gesture
        )
        return mov_gestures, mov_gestures_confidence

    def _accumulate_hand(self, method: str = "power_mean") -> np.array:
        """
        Accumulate the hand.

        Parameters
        ----------
        method: str
            The method to accumulate the hand. Can be either power_mean or
            sum.

        Returns
        -------
        accumulated_hand: np.array
            The accumulated hand.
        """
        # Get the accumulated hand.
        match method:
            case "power_mean":
                accumulated_hand = power_mean_frames(self.buffer_hand)
            case "sum":
                accumulated_hand = sum_frames(self.buffer_hand)
            case _:
                raise ValueError("Invalid method.")
        return accumulated_hand

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

    def set_model_search(ar_models: list[str]) -> bool:
        # set the models arr input.
        return True

    @staticmethod
    def get_gestures_names() -> np.array:
        """
        Get the names of the gestures.

        Returns
        -------
        gestures: np.array
            An array containing the names of the gestures.
        """
        return np.array(
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
        )
    
    @staticmethod
    def get_gestures_names_mov() -> np.array:
        """
        Get the names of the gestures with movements.

        Returns
        -------
        gestures: np.array
            An array containing the names of the gestures with movements.
        """
        return np.array(
            [
                "ten",
                "eleven",
                "twelve",
                "thirteen",
                "fourteen",
                "fifteen",
                "sixteen",
                "seventeen",
                "eighteen",
                "nineteen",
                "J",
            ]
        )

    @staticmethod
    def get_base_gestures(
        gestures: list[str],
        base_path: str = "./",
    ) -> dict[str, dict[str, np.array]]:
        """
        Get the base gestures.

        Parameters
        ----------
        gestures: list[str]
            A list containing the names of the gestures to load.
        base_path: str
            The path to the base gestures files.

        Returns
        -------
        base_gestures: dict[str,dict[str,np.array]]
            A dictionary containing the base gestures.
        """
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


def cosine_similarity(x: np.array, y: np.array, flatten: bool = False) -> float:
    """
    Compute the cosine similarity between two vectors.

    Parameters
    ----------
    x: np.array
        The first vector.
    y: np.array
        The second vector.
    flatten: bool = False
        A bool indicating if the vectors should be flattened.

    Returns
    -------
    cosine_similarity: float
        The cosine similarity between the two vectors.
    """
    if flatten:
        x = x.flatten()
        y = y.flatten()
        return 1 - np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))
    else:
        cos_sim = 0
        for x_el, y_el in zip(x, y):
            cos_sim += 1 - np.dot(x_el, y_el) / (
                np.linalg.norm(x_el) * np.linalg.norm(y_el) + 1e-6
            )
        return cos_sim / len(x)


def power_mean_frames(hand: np.array, p: float = 0) -> np.array:
    """
    Calculate the power mean of the hand.

    Parameters
    ----------
    hand: np.array
        The hand to calculate the power mean.
    p: float
        The power to calculate the power mean.

    Returns
    -------
    power_mean: np.array
        The power mean of the hand.
    """
    # Get the data in the hand frame of reference.
    hand_data_hand_frame = np.zeros_like(hand)
    for i in range(hand.shape[2]):
        hand_data_hand_frame[:, :, i] = np.abs(to_hand_frame(hand[:, :, i]))
    power_mean = pmean(hand_data_hand_frame, p, axis=2)
    # Is the best so far with p=0
    return power_mean


def sum_frames(hand_data: np.array, norm: bool = True) -> np.array:
    """
    Sum the frames of the hand data.

    Parameters
    ----------
    hand_data: np.array
        A 3D array containing the hand data video.
    norm: bool = True
        A bool indicating if the sum should be normalized.

    Returns
    -------
    summed: np.array
        A 2D array containing the sum of the frames.
    """
    summed = np.zeros((hand_data.shape[0], 3))
    for frame in range(hand_data.shape[2]):
        if norm:
            hand_data_hand_frame = to_hand_frame(hand_data[:, :3, frame])
        else:
            hand_data_hand_frame = hand_data[:, :3, frame]
        summed += hand_data_hand_frame
    return summed


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
# window.gesture = Gesture()
