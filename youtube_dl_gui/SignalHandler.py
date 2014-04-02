#! /usr/bin/env python

from .Utils import (
  remove_spaces,
  string_to_array
)

class DownloadHandler():
  
  def __init__(self, ListCtrl):
    self.ListCtrl = ListCtrl
    self.finished = False
    self.closed = False
    self.error = False
    self.handlers = []
  
  def _has_closed(self):
    return self.closed
 
  def _has_finished(self):
    return self.finished
    
  def _has_error(self):
    return self.error
 
  def handle(self, msg):
    ''' Handles msg base to Signals.txt '''
    pack = msg.data
    index = pack.index
    ''' Manage global index = -1 '''
    if index == -1:
      if pack.header == 'close':
	self.closed = True
      elif pack.header == 'finish':
	self.finished = True
    else:
      ''' Manage handlers for its index '''
      if index == len(self.handlers): 
	''' Create new IndexDownloadHandler and add it to handlers '''
	self.handlers.append(IndexDownloadHandler(self.ListCtrl, index))
      ''' Let IndexDownloadHandler handle message data for current index '''
      self.handlers[index].handle(pack)
      if self.handlers[index].has_error():
	self.error = True
 
class IndexDownloadHandler():
  
  def __init__(self, ListCtrl, index):
    self.ListCtrl = ListCtrl
    self.index = index
    self.err = False
    self.info = ''
  
  def has_error(self):
    return self.err
  
  def handle(self, pack):
    ''' Handle its pack for current index '''
    if pack.header == 'finish':
      self.finish()
    elif pack.header == 'close':
      self.close()
    elif pack.header == 'error':
      self.error()
    elif pack.header == 'playlist':
      self.playlist(pack.data)
    elif pack.header == 'youtube':
      self.pre_proc()
    elif pack.header == 'download':
      self.download(pack.data)
    elif pack.header == 'ffmpeg':
      self.post_proc()
    elif pack.header == 'remove':
      self.remove()
      
  def finish(self):
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Finished')
     
  def close(self):
    self.ListCtrl._write_data(self.index, 3, '')
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Stopped')
     
  def error(self):
    self.err = True
    self.ListCtrl._write_data(self.index, 3, '')
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Error')
     
  def pre_proc(self):
    self.ListCtrl._write_data(self.index, 5, 'Pre-Processing %s' % self.info)
     
  def post_proc(self):
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Post-Processing %s' % self.info)
     
  def download(self, data):
    self.ListCtrl._write_data(self.index, 1, data[0])
    self.ListCtrl._write_data(self.index, 2, data[1])
    self.ListCtrl._write_data(self.index, 3, data[2])
    self.ListCtrl._write_data(self.index, 4, data[3])
    self.ListCtrl._write_data(self.index, 5, 'Downloading %s' % self.info)
     
  def playlist(self, data):
    self.ListCtrl._write_data(self.index, 1, '')
    self.ListCtrl._write_data(self.index, 2, '')
    self.ListCtrl._write_data(self.index, 3, '')
    self.ListCtrl._write_data(self.index, 4, '')
    self.info = '%s/%s' % (data[0], data[1])
  
  def remove(self):
    self.ListCtrl._write_data(self.index, 5, 'Removing DASH Files')
  
class DataPack():
  
  def __init__(self, header, index=-1, data=None):
    self.header = header
    self.index = index
    self.data = data
    
class OutputHandler():
  
  def __init__(self, stdout):
    dataPack = None
    
    self.stdout = remove_spaces(string_to_array(stdout))
    # extract header from stdout
    header = self.extract_header()
    # extract special headers filename, playlist
    header = self.set_filename_header(header)
    header = self.set_playlist_header(header)
    # extract data base on header
    data = self.extract_data(header)
    # extract special ignore header base on header, data
    header = self.set_ignore_header(header, data)
    # create data pack 
    self.dataPack = DataPack(header, data=data)
  
  def extract_header(self):
    header = self.stdout.pop(0).replace('[', '').replace(']', '')
    return header
    
  def extract_data(self, header):
    ''' Extract data base on header '''
    if header == 'download':
      if '%' in self.stdout[0]:
	if self.stdout[0] != '100%':
	  ''' size, percent, eta, speed '''
	  return [self.stdout[2], self.stdout[0], self.stdout[6], self.stdout[4]]
    if header == 'playlist':
      return [self.stdout[2], self.stdout[4]]
    if header == 'filename':
      return ' '.join(self.stdout[1:])
    return None
  
  def set_filename_header(self, header):
    if header != 'ffmpeg':
      if self.stdout[0] == 'Destination:':
	return 'filename'
    return header
  
  def set_playlist_header(self, header):
    if header == 'download':
      if self.stdout[0] == 'Downloading' and self.stdout[1] == 'video':
	return 'playlist'
    return header
  
  def set_ignore_header(self, header, data):
    if header == 'download' and data == None:
      return 'ignore'
    return header
  
  def get_data(self):
    return self.dataPack
  
