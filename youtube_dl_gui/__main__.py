#!/usr/bin/env python2

''' Youtube-dlg __main__ file. '''

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path
    PATH = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(PATH)))

import youtube_dl_gui

if __name__ == '__main__':
    youtube_dl_gui.main()
