#! /usr/bin/env python

import subprocess
from time import sleep
from threading import Thread

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from .OutputHandler import (
  DataPack,
  OutputHandler
)

from .Utils import ( 
  get_encoding,
  encode_list,
  remove_file,
  get_os_type,
  file_exist
)

MAX_DOWNLOAD_THREADS = 3
PUBLISHER_TOPIC = 'download'

class DownloadManager(Thread):
  
  def __init__(self, options, downloadlist, clear_dash_files, logmanager=None):
    super(DownloadManager, self).__init__()
    self.clear_dash_files = clear_dash_files
    self.downloadlist = downloadlist
    self.logmanager = logmanager
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
	  proc = self.check_queue()
	  if proc != None:
	    self.procList.remove(proc)
	    self.procNo -= 1
	  sleep(1)
	# If we still running create new ProcessWrapper thread
	if self.running:
	  self.procList.append(
	    ProcessWrapper(
	      self.options,
	      url,
	      index,
	      self.clear_dash_files,
	      self.logmanager
	    )
	  )
	  self.procNo += 1
      else:
	# Return True if at least one process is alive else return False
	if not self.downloading():
	  self.running = False
	else:
	  sleep(0.1)
    # If we reach here close down all child threads
    self.terminate_all()
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, DataPack('finish'))
  
  def downloading(self):
    for proc in self.procList:
      if proc.isAlive():
	return True
    return False
  
  def _add_download_item(self, downloadItem):
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
    
  def check_queue(self):
    for proc in self.procList:
      if not self.running: break
      if not proc.isAlive():
	return proc
    return None
      
  def close(self):
    self.procNo = 0
    self.running = False
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, DataPack('close'))
    
class ProcessWrapper(Thread):
  
  def __init__(self, options, url, index, clear_dash_files, log=None):
    super(ProcessWrapper, self).__init__()
    self.clear_dash_files = clear_dash_files
    self.options = options
    self.index = index
    self.log = log
    self.url = url
    self.filenames = []
    self.stopped = False
    self.error = False
    self.proc = None
    self.start()
    
  def run(self):
    self.proc = self.create_process(self.get_cmd(), self.get_process_info())
    # while subprocess is alive and NOT the current thread
    while self.proc_is_alive():
      # read stdout, stderr from proc
      stdout, stderr = self.read()
      if stdout != '':
	# pass stdout to output handler
	data = OutputHandler(stdout).get_data()
	if self.clear_dash_files: self.add_file(data)
	# add index to data pack
	data.index = self.index
	# send data back to caller
	CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, data)
      if stderr != '':
	self.error = True
	self.write_to_log(stderr)
    if not self.stopped:
      if self.clear_dash_files:
	self.clear_dash()
      if not self.error:
	CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, DataPack('finish', self.index))
      else:
	CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, DataPack('error', self.index))  
  
  def add_file(self, dataPack):
    if dataPack.header == 'filename':
      self.filenames.append(dataPack.data)
  
  def write_to_log(self, data):
    if self.log != None:
      self.log.write(data)
  
  def clear_dash(self):
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, DataPack('remove', self.index))
    for f in self.filenames:
      if file_exist(f):
	remove_file(f)
    
  def close(self):
    self.proc.kill()
    self.stopped = True
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, DataPack('close', self.index))
  
  def proc_is_alive(self):
    return self.proc.poll() == None
  
  def read(self):
    stdout = ''
    stderr = ''
    stdout = self.proc.stdout.readline()
    if stdout == '':
      stderr = self.proc.stderr.readline()
    return stdout.rstrip(), stderr.rstrip()
  
  def create_process(self, cmd, info):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=info)
  
  def get_cmd(self):
    enc = get_encoding()
    if enc != None:
      cmd = encode_list(self.options + [self.url], enc)
    else:
      cmd = self.options + [self.url]
    return cmd
  
  def get_process_info(self):
    if get_os_type() == 'nt':
      info = subprocess.STARTUPINFO()
      info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      return info
    else:
      return None
      
