#!/usr/bin/env python2

"""Youtubedlg __main__ file.

__main__ file is a python 'executable' file which calls the youtubedlg
main() function in order to start the app. It can be used for starting
the app from inside the package OR it can be used for starting the app
from a different directory after you have installed the 
youtube_dl_gui package.

Example:
    In order to run the app from inside the package.
    
        $ cd <package director>
        $ python __main__.py
    
    In order to run the app from /usr/local/bin AFTER
    you have installed the package.
    
        $ youtube-dlg

"""

import sys

if __package__ is None and not hasattr(sys, "frozen"):
    # direct call of __main__.py
    import os.path
    PATH = os.path.realpath(os.path.abspath(__file__))
    sys.path.append(os.path.dirname(os.path.dirname(PATH)))

import youtube_dl_gui


if __name__ == '__main__':
    youtube_dl_gui.main()
