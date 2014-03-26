#! /usr/bin/env python

import os
from threading import Thread
from wx import CallAfter
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher
from urllib2 import urlopen, URLError, HTTPError

LATEST_YOUTUBE_DL = 'https://yt-dl.org/latest/'
PUBLISHER_TOPIC = 'update'
DOWNLOAD_TIMEOUT = 10

class UpdateThread(Thread):
  
  def __init__(self, youtubeDLFile):
    if os.name != 'nt':
      home_dir = os.path.expanduser('~')
      if not os.path.exists(home_dir + '/.cache/youtube-dl'):
        os.makedirs(home_dir + '/.cache/youtube-dl')
      os.chdir(home_dir + '/.cache/youtube-dl')
    super(UpdateThread, self).__init__()
    self.youtubeDLFile = youtubeDLFile
    self.url = LATEST_YOUTUBE_DL + youtubeDLFile
    self.start()
    
  def run(self):
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, "Downloading latest youtube-dl...")
    try:
      f = urlopen(self.url, timeout=DOWNLOAD_TIMEOUT)
      with open(self.youtubeDLFile, 'wb') as lf:
	lf.write(f.read())
      msg = 'Youtube-dl downloaded correctly'
    except (HTTPError, URLError, IOError) as e:
      msg = 'Youtube-dl download failed ' + str(e)
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, msg)
    CallAfter(Publisher.sendMessage, PUBLISHER_TOPIC, 'finish')
      