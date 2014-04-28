#! /usr/bin/env python

import os
import sys
import locale
import subprocess

def remove_empty_items(array):
  return [x for x in array if x != '']

def remove_spaces(string):
  return string.replace(' ', '')
  
def string_to_array(string, char=' '):
  return string.split(char)

def preferredencoding():
  try:
    pref = locale.getpreferredencoding()
    u'TEST'.encode(pref)
  except:
    pref = 'UTF-8'
  return pref
  
def get_encoding():
  if sys.version_info >= (3, 0):
    return None
  if sys.platform == 'win32':
    # Refer to http://stackoverflow.com/a/9951851/35070
    return preferredencoding()
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
  if path != '' and path[-1:] != get_path_seperator():
      path += get_path_seperator()
  return path
  
def get_HOME():
  return os.path.expanduser("~")
  
def add_PATH(path):
  os.environ["PATH"] += os.pathsep + path

def abs_path(path):
  path_list = path.split(get_path_seperator())
  for i in range(len(path_list)):
    if path_list[i] == '~':
      path_list[i] = get_HOME()
  return get_path_seperator().join(path_list)
  
def file_exist(filename):
  return os.path.exists(filename)
  
def get_os_type():
  return os.name
 
def get_filesize(path):
  return os.path.getsize(path)
 
def makedir(path):
  os.makedirs(path)
  
def get_filename(path):
  return path.split(get_path_seperator())[-1]
  
def open_dir(path):
  if os.name == 'nt':
    os.startfile(path)
  else:
    subprocess.call(('xdg-open', path))
  
