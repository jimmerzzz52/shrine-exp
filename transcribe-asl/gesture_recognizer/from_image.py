# The idea here is that we input an image, and compare it to the database of gestures.


def from_image_get_dataframe(image_source):
  # TODO: sense the image source. file, url, bit array...
  # get the image, get the xyz coordinates using mediapipe.
  # compare this to our dictionary of gestures....