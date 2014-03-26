#! /usr/bin/env python

import subprocess
from time import sleep
from wx import CallAfter
from threading import Thread
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .Utils import ( 
  remove_spaces,
  string_to_array,
  get_encoding,
  encode_list,
  remove_file,
  get_os_type
)

MAX_DOWNLOAD_THREADS = 3
PUBLISHER_TOPIC = 'download'

class DownloadManager(Thread):
  
  def __init__(self, options, downloadlist, clear_dash_files):
    super(DownloadManager, self).__init__()
    self.clear_dash_files = clear_dash_files
    self.downloadlist = downloadlist
    self.options = options
    self.running = True
    self.procList = []
    self.procNo = 0
    self.start()
    
  def run(self):
    while self.running:
      if self.downloadlist:
	# Extract url, index from data
	url, index = self.extract_data()
	# Wait for your turn if there are not more positions in 'queue'
	while self.procNo >= MAX_DOWNLOAD_THREADS:
	  proc = self.check_queue(0.5)
	  if proc != None:
	    self.procList.remove(proc)
	    self.procNo -= 1
	# If we still running create new ProcessWrapper thread
	if self.running:
	  self.procList.append(
	    ProcessWrapper(
	      self.options,
	      url,
	      index,
	      self.clear_dash_files
	    )
	  )
	  self.procNo += 1
      else:
	# Return True if at least one process is alive else return False
	if not self.downloading():
	  self.running = False
	else:
	  sleep(1)
    
    # If we reach here close down all child threads
    self.terminate_all()
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['finish', -1])
  
  def add_download_item(self, downloadItem):
    self.downloadlist.append(downloadItem)
    
  def extract_data(self):
    data = self.downloadlist.pop(0)
    url = data['url']
    index = data['index']
    return url, index
    
  def terminate_all(self):
    for proc in self.procList:
      if proc.isAlive():
	proc.close()
	proc.join()
    
  def downloading(self):
    for proc in self.procList:
      if proc.isAlive():
	return True
    return False

  def check_queue(self, t=1):
    for proc in self.procList:
      if not self.running: break
      if not proc.isAlive():
	return proc
      sleep(t)
    return None
      
  def close(self):
    self.procNo = 0
    self.running = False
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['close', -1])
    
class ProcessWrapper(Thread):
  
  def __init__(self, options, url, index, clear_dash_files):
    super(ProcessWrapper, self).__init__()
    self.clear_dash_files = clear_dash_files
    self.options = options
    self.index = index
    self.url = url
    self.filenames = []
    self.proc = None
    self.stopped = False
    self.err = False
    self.start()
    
  def run(self):
    self.proc = subprocess.Popen(self.get_cmd(), 
				 stdout=subprocess.PIPE,
				 stderr=subprocess.PIPE,
				 startupinfo=self.set_process_info())
    # while subprocess is alive and NOT the current thread
    while self.proc_is_alive():
      # read output
      output = self.read()
      if output != '':
	# process output
	data = self.proc_output(output)
	if self.err:
	  CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['error', self.index])
	else:
	  CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, data)
    if not self.err and not self.stopped:
      if self.clear_dash_files: 
	self.cleardash()
      CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['finish', self.index])
    
  def extract_filename(self, data):
    data_list = data.split(':')
    if 'Destination' in data_list[0].split():
      self.filenames.append(data_list[1].lstrip())
    
  def cleardash(self):
    if self.filenames:
      CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['remove', self.index])
      for f in self.filenames:
	remove_file(f)
    
  def close(self):
    self.proc.kill()
    self.stopped = True
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['close', self.index])
  
  def proc_is_alive(self):
    return self.proc.poll() == None
  
  def read(self):
    output = self.proc.stdout.readline()
    if output == '':
      output = self.proc.stderr.readline()
      if output != '':
	self.err = True
    return output.rstrip()
    
  def proc_output(self, output):
    if self.clear_dash_files:
      self.extract_filename(output)
    data = remove_spaces(string_to_array(output))
    data.append(self.index)
    data = self.filter_data(data)
    return data
    
  def filter_data(self, data):
    ''' Filters data for output exceptions '''
    filter_list = ['Destination:', '100%', 'Resuming']
    if len(data) > 3: 
      if data[0] == '[download]':
	if data[1] in filter_list or len(data[1]) > 11:
	  return ['ignore', self.index]
	if data[1] == 'Downloading':
	  if data[2] == 'video':
	    return ['playlist', data[3], data[5], self.index]
	  else:
	    return ['ignore', self.index]
      else:
	if data[1] == 'UnicodeWarning:':
	  self.err = False
	  return ['ignore', self.index]
    return data
    
  def get_cmd(self):
    enc = get_encoding()
    if enc != None:
      data = encode_list(self.options + [self.url], enc)
    return self.options + [self.url]
  
  def set_process_info(self):
    if get_os_type() == 'nt':
      info = subprocess.STARTUPINFO()
      info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      return info
    else:
      return None
      