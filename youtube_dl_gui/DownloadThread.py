#! /usr/bin/env python

import subprocess
from os import name
from time import sleep
from wx import CallAfter
from threading import Thread
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

OS_TYPE = name
MAX_DOWNLOAD_THREADS = 3
PUBLISHER_TOPIC = 'download'

class DownloadManager(Thread):
  
  def __init__(self, options, downloadlist):
    super(DownloadManager, self).__init__()
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
	  self.procList.append(ProcessWrapper(self.options, url, index))
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
      if not self.running:
	break
      if not proc.isAlive():
	return proc
      sleep(t)
    return None
      
  def close(self):
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['close', -1])
    self.running = False
    self.procNo = 0
    
class ProcessWrapper(Thread):
  
  def __init__(self, options, url, index):
    super(ProcessWrapper, self).__init__()
    self.options = options
    self.index = index
    self.url = url
    self.proc = None
    self.info = None
    self.err = False
    self.stopped = False
    self.set_process_info()
    self.start()
    
  def run(self):
    self.proc = subprocess.Popen(self.options + [self.url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=self.info)
    # while subprocess is alive and NOT the current thread
    while self.proc_is_alive():
      # read output
      output = self.read()
      if output != '':
	data = self.proc_output(output)
	data = self.check_data(data)
	if self.err:
	  CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['error', self.index])
	else:
	  CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, data)
    if not self.err and not self.stopped:
      CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['finish', self.index])
    
  def close(self):
    self.proc.kill()
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, ['close', self.index])
    self.stopped = True
  
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
    data = self.remove_spaces(self.string_to_array(output))
    data.append(self.index)
    return data
    
  def check_data(self, data):
    ''' check data for exceptions '''
    if len(data) > 3: 
      if data[1] == "UnicodeWarning:":
	self.err = False
	return ['ignore']
      if data[0] == "[download]" and data[1] == "Destination:":
	return ['ignore']
      if data[0] == "[download]" and data[1] == "100%":
	return ['ignore']
    return data
    
  def string_to_array(self, string):
    return string.split(' ')
    
  def remove_spaces(self, array):
    return [x for x in array if x != '']
    
  def set_process_info(self):
    if OS_TYPE == 'nt':
      self.info = subprocess.STARTUPINFO()
      self.info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      