import pytest
import unittest


class TestGestureRecognizer(unittest.TestCase):

  def test_no_gesture(self):
    self.assertEqual('foo'.upper(), 'FOO')

  def test_random(self):
    # TODO: randomly
    self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()