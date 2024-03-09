# A data class the recognizes one....

# TODO: create method for video, url, image and other...
# TODO: move into the init function so we do not have to import on every one...

# from functools import singledispatch
# import re
# import urllib.request
import pandas as pd


# IS_WEBSITE_REGULAR_EXPRESSION_WITHOUT_HTTP = '[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'


# def _isURL(input_:str):
#   return re.search(_input, IS_WEBSITE_REGULAR_EXPRESSION_WITHOUT_HTTP)

# def _recognize_url(url:str):
#   file_path = _download_url(url)
  
# def _download_url(url: str):
#   file_extension = pathlib.Path(url).suffix
#   urllib.request.urlretrieve(url, file_extension)
#   return f'./downloaded/{url}'

def recognize_dataframe(dataframe: pd.Dataframe):
  arr = dataframe.to_numpy()
  
  # check to see if first finger is pointed upward...
  
  
  
  
# @singledispatch
def recognize(input_):
  if isinstance(input_x, pd.DataFrame):
    recognize_dataframe(dataframe)

# @recognize.register
# def _(input_: str):
#   if _isURL:
#     _recognize_url(input_)
#   else:
#     print("We do not recognize anything else")
  
# @recognize.register
# def _(input_: dict):
#   print("you gave a dict-like input")
  