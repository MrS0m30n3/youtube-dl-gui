#! /usr/bin/env python

import os
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
  
def video_is_dash(video):
  return "DASH" in video
  
def have_dash_audio(audio):
  return audio != "NO SOUND"
  
def remove_file(filename):
  os.remove(filename)

def get_path_seperator():
  if os.name == 'nt':
    return '\\'
  else:
    return '/'
  
def fix_path(path):
  if path != '':
    if path[-1:] != get_path_seperator():
      path += get_path_seperator()
  return path
  
def get_HOME():
  return os.path.expanduser("~")
  
def add_PATH(path):
  os.environ["PATH"] += os.pathsep + path

def get_abs_path(path):
  sep = get_path_seperator()
  path_list = path.split(sep)
  for i in range(len(path_list)):
    if path_list[i] == '~':
      path_list[i] = get_HOME()
  path = sep.join(path_list)
  return path
  
def file_exist(filename):
  return os.path.exists(filename)
  
def get_os_type():
  return os.name
  
def makedir(path):
  os.makedirs(path)
  
