#! /usr/bin/env python

from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher

from threading import Thread
from urllib2 import urlopen, URLError, HTTPError

from .Utils import (
  fix_path,
  file_exist,
  makedir
)

LATEST_YOUTUBE_DL = 'https://yt-dl.org/latest/'
PUBLISHER_TOPIC = 'update'
DOWNLOAD_TIMEOUT = 20

class UpdateThread(Thread):
  
  def __init__(self, updatePath, youtubeDLFile):
    super(UpdateThread, self).__init__()
    self.youtubeDLFile = youtubeDLFile
    self.updatePath = fix_path(updatePath)
    self.url = LATEST_YOUTUBE_DL + youtubeDLFile
    self.check_path()
    self.start()
    
  def run(self):
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, "Downloading latest youtube-dl. Please wait...")
    try:
      f = urlopen(self.url, timeout=DOWNLOAD_TIMEOUT)
      with open(self.updatePath + self.youtubeDLFile, 'wb') as lf:
	lf.write(f.read())
      msg = 'Youtube-dl downloaded correctly'
    except (HTTPError, URLError, IOError) as e:
      msg = 'Youtube-dl download failed ' + str(e)
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, msg)
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, 'finish')

  def check_path(self):
    if not file_exist(self.updatePath):
      makedir(self.updatePath)
      
