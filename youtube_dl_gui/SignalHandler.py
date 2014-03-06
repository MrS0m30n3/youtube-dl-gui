#! /usr/bin/env python

class DownloadHandler():
  
  def __init__(self, ListCtrl):
    self.ListCtrl = ListCtrl
    self.finished = False
    self.close = False
    self.handlers = []
  
  def _has_closed(self):
    return self.close
 
  def _has_finished(self):
    return self.finished
 
  def handle(self, msg):
    ''' Handles msg base to Signals.txt '''
    data = msg.data
    index = self.get_index(data)
    if index == -1:
      if data[0] == 'finish':
	self.finished = True
      elif data[0] == 'close':
	self.close = True
    else:
      ''' Manage handlers for its index '''
      if index == len(self.handlers): 
	''' Create new IndexDownloadHandler and add it to handlers '''
	self.handlers.append(IndexDownloadHandler(self.ListCtrl, index))
      ''' Let IndexDownloadHandler handle message data for current index '''
      self.handlers[index].handle(data)
  
  def get_index(self, data):
    return data.pop()
      
class IndexDownloadHandler():
  
  def __init__(self, ListCtrl, index):
    self.ListCtrl = ListCtrl
    self.index = index
    self.info = ''
    
  def handle(self, data):
    ''' Handle its data message for current index '''
    if data[0] == 'finish':
      self.finish()
    elif data[0] == 'close':
      self.close()
    elif data[0] == 'error':
      self.error()
    elif data[0] == 'playlist':
      self.playlist(data)
    elif data[0] == '[youtube]':
      self.pre_proc()
    elif data[0] == '[download]':
      self.download(data)
    elif data[0] == '[ffmpeg]':
      self.post_proc()
      
  def finish(self):
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Finished')
     
  def close(self):
    self.ListCtrl._write_data(self.index, 3, '')
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Stopped')
     
  def error(self):
    self.ListCtrl._write_data(self.index, 3, '')
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Error')
     
  def pre_proc(self):
    self.ListCtrl._write_data(self.index, 5, 'Pre-Processing %s' % self.info)
     
  def post_proc(self):
    self.ListCtrl._write_data(self.index, 4, '')
    self.ListCtrl._write_data(self.index, 5, 'Converting to Audio %s' % self.info)
     
  def download(self, data):
    self.ListCtrl._write_data(self.index, 1, data[3])
    self.ListCtrl._write_data(self.index, 2, data[1])
    self.ListCtrl._write_data(self.index, 3, data[7])
    self.ListCtrl._write_data(self.index, 4, data[5])
    self.ListCtrl._write_data(self.index, 5, 'Downloading %s' % self.info)
     
  def playlist(self, data):
    self.ListCtrl._write_data(self.index, 1, '')
    self.ListCtrl._write_data(self.index, 2, '')
    self.ListCtrl._write_data(self.index, 3, '')
    self.ListCtrl._write_data(self.index, 4, '')
    self.info = '%s/%s' % (data[1], data[2])
      