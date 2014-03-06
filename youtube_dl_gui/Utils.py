#! /usr/bin/env python

import sys

def remove_spaces(array):
  return [x for x in array if x != '']
  
def string_to_array(string, char=' '):
  return string.split(char)
  
def get_encoding():
  if sys.version_info >= (3, 0):
    return None
    
  if sys.platform == 'win32':
    return sys.getfilesystemencoding()
  else:
    return None
    
def encode_list(data_list, encoding):
  return [x.encode(encoding, 'ignore') for x in data_list]
  