#! /usr/bin/env python

import wx

from time import strftime
from .Utils import (
  fix_path,
  file_exist,
  get_filesize
)

LOG_FILENAME = 'log'
LOG_FILESIZE = 524288 # 524288B = 512kB

class LogManager():
  
  def __init__(self, path, add_time=False):
    self.path = fix_path(path) + LOG_FILENAME
    self.add_time = add_time
    self.init_log()
    self.check_log()
  
  def check_log(self):
    if self.log_size() > LOG_FILESIZE:
      self.clear()
  
  def init_log(self):
    if not file_exist(self.path):
      self.clear()
  
  def log_size(self):
    return get_filesize(self.path)
  
  def clear(self):
    with open(self.path, 'w') as fl:
      fl.write('')
  
  def write(self, data):
    with open(self.path, 'a') as fl:
      if self.add_time: 
	t = '[%s] ' % strftime('%c')
	fl.write(t)
      fl.write(data)
      fl.write('\n')
   
class LogGUI(wx.Frame):
  
  title = 'Log Viewer'
  
  def __init__(self, path, parent=None, id=-1):
    wx.Frame.__init__(self, parent, id, self.title, size=(650, 200))
    
    panel = wx.Panel(self)
    textArea = wx.TextCtrl(panel, -1, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
    sizer = wx.BoxSizer()
    sizer.Add(textArea, 1, wx.EXPAND)
    panel.SetSizerAndFit(sizer)
    
    textArea.LoadFile(path)
    
