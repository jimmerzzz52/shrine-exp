import pandas as pd
import numpy as np
from typing import Optional
from sklearn.preprocessing import MinMaxScaler


class Gesture:

    def __init__(
        self,
        right: Optional[np.array] = None,
        left: Optional[np.array] = None,
        body: Optional[np.array] = None,
    ):
        """
        Initialize the Gesture object.
        """
        self.right: Optional[np.array] = right
        self.left: Optional[np.array] = left
        self.body: Optional[np.array] = body

    def fit(self):
        # TODO: Add all of the poses here...

        # For The pose one, all we need is the right hand.
        if self.right is None and self.left is None:
            return "Nothing recognized"

        # It's a cascade of poses.... First start with one then it drills down into the other ones.
        if self.right is not None:
            # if self._is_pointed_finger():
            #     return "Pointed Finger!"
            if self._is_one():
                return "One!"
            if self._is_two():
                return "Two!"

    def _is_pointed_finger(self) -> bool:
        """
        Check if the hand is in the pointed finger pose.

        Returns
        -------
        is_pointed_finger: bool
            A bool indicating if the hand is in the pointed finger pose.
        """
        df = pd.DataFrame(
            self.right, columns=["x", "y", "z"]
        )  # isn't this x, y, z? YES!

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

    def _is_one(self) -> bool:
        """
        Check if the hand is in the one pose.

        Returns
        -------
        is_one: bool
            A bool indicating if the hand is in the one pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            np.genfromtxt(
                "./gesture/base_poses_hf/one_Transcription_Right_Hand.csv",
                delimiter=",",
            )[1:, 1:]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(self.right)
        # match the points.
        return match_position_points(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )

    def _is_two(self) -> bool:
        """
        Check if the hand is in the two pose.

        Returns
        -------
        is_one: bool
            A bool indicating if the hand is in the one pose.
        """
        # Load the base points in the hand frame of reference.
        base_points_in_hand_frame: np.array = to_hand_frame(
            np.genfromtxt(
                "./gesture/base_poses_hf/two_Transcription_Right_Hand.csv",
                delimiter=",",
            )[1:, 1:]
        )
        # get the incoming poitns in the hand frame of reference.
        incoming_points_in_hand_frame: np.array = to_hand_frame(self.right)
        # match the points.
        return match_position_points(
            base_points_in_hand_frame, incoming_points_in_hand_frame
        )


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


def to_hand_frame(coordinates: np.array) -> np.array:
    """Rotate and translates the coordinates to the hand frame of reference.

    Inputs:
        coordinates: np.array
            A 2D array containing the coordinates of the points to rotate.

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
