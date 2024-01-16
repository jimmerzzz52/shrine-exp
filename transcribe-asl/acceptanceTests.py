# Loop through a list of images, compare the output with the alg. Compare the output to what is defined.


# How do we handle not still images? Do we train on not still images? Classification


import glob
import pandas as pd

mypath = './gestures'

print(glob.glob("./gestures/ONE.csv"))
gesture_files = glob.glob("./gestures/ONE*.csv")

# start at the first five.. TODO: remove
for indx, gesture_file in enumerate(gesture_files):
  if indx > 2:
    break
  print(gesture_file)
  df = pd.read_csv(gesture_file)
  
  print(df.head())
  # Get the middle value.
  print(df['time'].astype('datetime64[ns]').quantile(0.5, interpolation="midpoint"))
  from terminalplot import plot
  plot(df['x'], df['y'])
  print(df.columns)