import pandas as pd
import numpy as np
from typing import Optional


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
        if base_gestures is None:
            self.base_gestures: dict[str, dict[str, np.array]] = (
                Gesture.get_base_gestures()
            )
        else:
            self.base_gestures = base_gestures
        # Note to self: this class should be loaded outside the loop, initialized with the data in the database and then
        # the fit method should be called in the loop with right, left, and body data as the parameters.
        # fit should be called predict.

    def predict(
        self,
        right: Optional[np.array] = None,
        left: Optional[np.array] = None,
        body: Optional[np.array] = None,
    ):
        # TODO: Add all of the poses here...

        # For The pose one, all we need is the right hand.
        if right is None and left is None:
            return "Nothing recognized"

        # It's a cascade of poses.... First start with one then it drills down into the other ones.
        if right is not None:
            errors = {
                "one": self._one(right),
                "two": self._two(right),
                "three": self._three(right),
                "four": self._four(right),
                "five": self._five(right),
            }
            smaller = min(
                errors, key=errors.get
            )  # The identified pose is the one with the smallest error.
            return smaller

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

    def _one(self, right: Optional[np.array]) -> float:
        """
        Check the error with the one pose.

        Parameters
        ----------
        right: np.array
            The points of the right hand.

        Returns
        -------
        error: float
            The error with the one pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            self.base_gestures["one"]["right_hand"]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(right)
        # match the points.
        return mean_squared_error(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

    def _two(self, right: Optional[np.array]) -> bool:
        """
        Check the error with the two pose.

        Parameters
        ----------
        right: np.array
            The points of the right hand.

        Returns
        -------
        error: float
            The error with the two pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            self.base_gestures["two"]["right_hand"]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(right)
        # match the points.
        return mean_squared_error(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

    def _three(self, right: Optional[np.array]) -> bool:
        """
        Check the error with the three pose.

        Parameters
        ----------
        right: np.array
            The points of the right hand.

        Returns
        -------
        error: float
            The error with the three pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            self.base_gestures["three"]["right_hand"]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(right)
        # match the points.
        return mean_squared_error(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

    def _four(self, right: Optional[np.array]) -> bool:
        """
        Check the error with the four pose.

        Parameters
        ----------
        right: np.array
            The points of the right hand.

        Returns
        -------
        error: float
            The error with the four pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            self.base_gestures["four"]["right_hand"]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(right)
        # match the points.
        return mean_squared_error(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

    def _five(self, right: Optional[np.array]) -> bool:
        """
        Check the error with the five pose.

        Parameters
        ----------
        right: np.array
            The points of the right hand.

        Returns
        -------
        error: float
            The error with the five pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            self.base_gestures["five"]["right_hand"]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(right)
        # match the points.
        return mean_squared_error(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

    @staticmethod
    def get_base_gestures() -> dict[str, dict[str, np.array]]:
        """
        Get the base gestures.

        Returns
        -------
        base_gestures: dict[str,dict[str,np.array]]
            A dictionary containing the base gestures.
        """
        # Define the base gestures path
        base_path: str = "./gesture/base_poses_hf"
        # Define the gestures.
        gestures: list[str] = ["one", "two", "three", "four", "five"]
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
