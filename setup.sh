#!/bin/bash -i
# Fail on errors.
set -e

# Install pre-requirements like wxPython
# on PyInstaller ManyLinux 2014 Docker Action
wget https://extras.wxpython.org/wxPython4/extras/linux/gtk3/centos-7/wxPython-4.1.0-cp36-cp36m-linux_x86_64.whl
pip3 install wxPython-4.1.0-cp36-cp36m-linux_x86_64.whl
