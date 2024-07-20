"""
This file implements a script that transform the csv database into a numpy a saved numpy array.
"""

import os
import numpy as np
import pandas as pd


def get_data_in_time(one_data_test, time=None):
    one_data_test = one_data_test.copy()
    one_data_test["time"] = pd.to_datetime(one_data_test["time"], format="%H:%M:%S.%f")
    one_data_test["time"] = one_data_test["time"] - one_data_test["time"][0]
    one_data_test["time"] = one_data_test["time"].dt.total_seconds()
    # Filter to get only the data of the one signal
    if time is not None:
        one_data_test = one_data_test[one_data_test["time"] >= time[0]]
        one_data_test = one_data_test[one_data_test["time"] <= time[1]]
        one_data_test["time"] = one_data_test["time"] - one_data_test["time"].iloc[0]
    # And transform it to the same shape as the one_base
    one_test_ni = []
    for index in range(21):
        index_data = one_data_test[one_data_test["index"] == index]
        index_data = index_data.sort_values(by="time")
        one_test_ni.append(
            [
                index_data["x"].values,
                index_data["y"].values,
                index_data["z"].values,
                index_data["time"].values,
            ]
        )
    one_test_ni = np.array(one_test_ni)
    return one_test_ni


# Path to the csv files
path = "./gesture_data"
# Path to the numpy files
path_np = "./gesture/base_poses_hf"

# List of the csv files
files = os.listdir(path)

files_to_get = [
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
    "twenty",
    "twenty_one",
    "twenty_two",
    "twenty_three",
    "twenty_four",
    "twenty_five",
    "twenty_six",
    "twenty_seven",
    "twenty_eight",
    "twenty_nine",
    "thirty",
    "thirty_one",
    "thirty_two",
    "thirty_three",
    "thirty_four",
    "thirty_five",
    "thirty_six",
    "thirty_seven",
    "thirty_eight",
    "thirty_nine",
    "forty",
    "j",
    "z",
]

# Get the files that are in the files_to_get list
files = [
    file
    for file in files
    if file.split("_")[0].lower() in files_to_get
    if "1" not in file.split("_")
]

# Iterate over the files
for file in files:
    file_pd = pd.read_csv(f"{path}/{file}", parse_dates=True)
    if file_pd.shape[0] > 0:
        # Transform the data into a numpy array
        np_file = get_data_in_time(file_pd)
        # Save the numpy array
        np.save(f"{path_np}/{file[:-4]}.npy", np_file)
