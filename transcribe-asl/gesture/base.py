import pandas as pd
import numpy

class Gesture:
  
  # def __init__(self):
  
  def fit(self, right=None, left=None, body=None):
    # TODO: Add all of the poses here...
    
    # For The pose one, all we need is the right hand.
    if right == None and left == None:
      return "Nothing recognized"
    
    
    # It's a cascade of poses.... First start with one then it drills down into the other ones.
    if right != None:

      df = pd.DataFrame(right,  columns =['y', 'x', 'z'])
      
      print(df)
      index_finger_height = df['y'].iloc[8]
      max_limb_height = df.nlargest(1, 'y')['y'].iloc[0]
      print(df.nlargest(1, 'y'))
      print(index_finger_height)
      
      if index_finger_height == max_limb_height:
        return "Pointed Finger!"
    