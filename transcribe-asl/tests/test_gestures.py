import pytest
import unittest
# TODO import the gesture base...
from ..gesture.base import Gesture

class TestGestureRecognizer(unittest.TestCase):

  def test_no_gesture(self):
    self.assertEqual('foo'.upper(), 'FOO')

  def test_random(self):
    # TODO: randomly choose a gesture, 
    # run it through the algorithm. 
    # Make sure it identifies the pose name.
    self.assertEqual('foo'.upper(), 'FOO')

  def test_a_gesture():
    # Get data from test store.. Handspeak.
    Gesture.classify()
    



if __name__ == '__main__':
    unittest.main()