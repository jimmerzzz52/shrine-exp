import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime, timedelta


class Gesture:

    def __init__(
        self,
        base_gestures: Optional[dict[str, dict[str, np.array]]] = None,
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
        self.gestures: list[list[str]] = [
            ["one"],
            ["two"],
            ["three"],
            ["four"],
            ["five"],
            ["six"],
            ["seven"],
            ["eight"],
            ["nine"],
            ["ten_1", "ten_2", "ten_3"],
        ]
        if base_gestures is None:
            self.base_gestures: dict[str, dict[str, np.array]] = (
                Gesture.get_base_gestures(self.gestures)
            )
        else:
            self.base_gestures = base_gestures

        self.gesture_movie_array = [
            gesture for gesture in self.gestures if len(gesture) > 1
        ]
        self.check_point = 0
        self.check_point_time = datetime.now() - timedelta(seconds=60)

    def predict(
        self,
        right: Optional[np.array] = None,
        left: Optional[np.array] = None,
        body: Optional[np.array] = None,
    ) -> str:
        """
        Predict the pose of the person.

        Parameters
        ----------
        right: np.array
            The points of the right hand.
        left: np.array
            The points of the left hand.
        body: np.array
            The points of the body.

        Returns
        -------
        pose: str
            The pose of the person.
        """
        # Reset the check points.
        self._reset_check_points(wait_seconds=5)
        # For The pose one, all we need is the right hand.
        if right is None and left is None:
            return "Nothing recognized"

        # It's a cascade of poses.... First start with one then it drills down into the other ones.
        if right is not None:
            # Poses are static, so we can compare the points directly.
            poses_names = [
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
                "ten",
            ]
            errors_poses = {
                pose_name: self._compare_hand_check_points(
                    self.base_gestures[pose_name]["right_hand"], right
                )
                for pose_name in poses_names
            }
            movs_names = ["ten"]
            errors_movs = {
                mov_name: self._compare_hand_movement(
                    self.base_gestures[mov_name]["right_hand"], right
                )
                for mov_name in movs_names
            }
            errors = errors_poses | errors_movs  # merge the two dictionaries
            smaller = min(
                errors, key=errors.get
            )  # The identified pose is the one with the smallest error.
            print(self.check_point)
            if smaller in movs_names:
                if (
                    self.check_point
                    < self.base_gestures[smaller]["right_hand"].shape[2] - 1
                ):
                    return "Identifying hand movement"
                else:
                    return smaller
            else:
                return smaller
        if left is None:
            return "Nothing recognized"

    def _is_pointed_finger(self, right: Optional[np.array]) -> bool:
        """
        Check if the hand is in the pointed finger pose.

        Returns
        -------
        is_pointed_finger: bool
            A bool indicating if the hand is in the pointed finger pose.
        """
        df = pd.DataFrame(right, columns=["x", "y", "z"])  # isn't this x, y, z? YES!

        print(df)
        index_finger_height = df["y"].iloc[8]
        max_limb_height = df.nlargest(1, "y")["y"].iloc[0]
        print(df.nlargest(1, "y"))
        print(index_finger_height)

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
        base_points_in_hand_frame: np.array = to_hand_frame(base_points)
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(incoming_points)
        # match the points.
        return mean_squared_error(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

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
        for i, gestures_movie in enumerate(self.gesture_movie_array):
            if (
                self.check_point[i] < len(gestures_movie)
                and gesture == gestures_movie[self.check_point[i]]
            ):
                self.check_point[i] += 1
                self.check_point_time[i] = datetime.now()  # ?

    def _reset_check_points(self, wait_seconds: int = 5):
        """
        Reset the check points.
        """
        # Reset the check point if it's been too long.
        if datetime.now() - self.check_point_time > timedelta(seconds=wait_seconds):
            self.check_point = 0  # np.zeros(len(self.base_gestures))
            self.check_point_time = datetime.now() - timedelta(seconds=60)

    @staticmethod
    def get_base_gestures(gestures: list[list[str]]) -> dict[str, dict[str, np.array]]:
        """
        Get the base gestures.

        Returns
        -------
        base_gestures: dict[str,dict[str,np.array]]
            A dictionary containing the base gestures.
        """
        # Define the base gestures path
        base_path: str = "./gesture/base_poses_hf"
        # Load the base gestures from the database.
        base_gestures: dict[str, dict[str, np.array]] = {}
        for list_gesture in gestures:
            if len(list_gesture) == 1:
                gesture = list_gesture[0]
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
            else:
                right_hand: list[np.array] = []
                left_hand: list[np.array] = []
                pose: list[np.array] = []
                for gesture in list_gesture:
                    right_hand.append(
                        load_base_gesture(
                            f"{base_path}/{gesture}_Transcription_Right_Hand.csv"
                        )
                    )
                    left_hand.append(
                        load_base_gesture(
                            f"{base_path}/{gesture}_Transcription_Left_Hand.csv"
                        )
                    )
                    pose.append(
                        load_base_gesture(
                            f"{base_path}/{gesture}_Transcription_Pose.csv"
                        )
                    )
                gesture_name = list_gesture[0].split("_")[0]
                base_gestures[gesture_name] = {
                    "right_hand": concat_or_none(right_hand),
                    "left_hand": concat_or_none(left_hand),
                    "pose": concat_or_none(pose),
                }
        return base_gestures


def concat_or_none(array: list[np.array]) -> Optional[np.array]:
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


def load_base_gesture(path: str) -> Optional[np.array]:
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
        return base_gesture[1:, 1:, np.newaxis]
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


# auxillary functions (Not sure they should be here or not but I think it deserves its own file)
def hand_frame_of_reference(coordinates: np.array) -> np.array:
    """Get the hand frame of reference.

    Inputs:
        coordinates: np.array
            A 2D array containing the coordinates of the points.
            Coordinates are expected to be sorted according to their index.

    Outputs:
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

    Inputs:
        coordinates: np.array
            A 2D array containing the coordinates of the points to rotate.
        norm: bool
            A bool indicating if the coordinates should be normalized.

    Outputs:
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
    if norm:
        # The coordinates are normalized by dividing them by the maximum absolute value of the coordinates.
        coordinates_hand_frame = coordinates_hand_frame / np.abs(
            coordinates_hand_frame
        ).max(axis=0)
    return coordinates_hand_frame


def match_position_points(base_points: np.array, points: np.array) -> np.array:
    """Match the position of the points to the base points.

    Inputs:
        base_points: np.array
            A 2D array containing the base points in the hand frame of reference.
        points: np.array
            A 2D array containing the points to match in the hand frame of reference.

    Outputs:
        points_matched: bool
            A bool indicating if the points were matched.

    Note: For this to work properly, the points should be in the hand frame of reference.
    """

    return np.allclose(base_points, points, atol=9e-2)
