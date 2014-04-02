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
  return '\\' if os.name == 'nt' else '/'
  
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
  path_list = path.split(get_path_seperator())
  for i in range(len(path_list)):
    if path_list[i] == '~':
      path_list[i] = get_HOME()
  path = get_path_seperator().join(path_list)
  return path
  
def file_exist(filename):
  return os.path.exists(filename)
  
def get_os_type():
  return os.name
 
def get_filesize(path):
  return os.path.getsize(path)
 
def makedir(path):
  os.makedirs(path)
  
def get_icon_path(icon_path, file_path):
  path = os.path.abspath(file_path)
  path = path.split(get_path_seperator())
  for i in range(len(icon_path)):
    path[(i+1)*-1] = icon_path[i]
  path = get_path_seperator().join(path)
  return path
  
  
