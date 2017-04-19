#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtube-dlg setup file.

Examples:
    Windows::

        python setup.py py2exe

    Linux::

        python setup.py install

    Build source distribution::

        python setup.py sdist

    Build platform distribution::

        python setup.py bdist

    Build the translations::

        python setup.py build

Requirements:

    * GNU gettext utilities

Notes:
    If you get 'TypeError: decoding Unicode is not supported' when you run
    py2exe then apply the following patch::

        http://sourceforge.net/p/py2exe/patches/28/

    Basic steps of the setup::

        * Run pre-build tasks
        * Call setup handler based on OS & options
            * Set up hicolor icons (if supported by platform)
            * Set up fallback pixmaps icon (if supported by platform)
            * Set up package level pixmaps icons (*.png, *.ico)
            * Set up package level i18n files (*.mo)
            * Set up scripts (executables) (if supported by platform)
        * Run setup

"""

from distutils.core import setup

import os
import sys
import glob
from shutil import copyfile
from subprocess import call

PY2EXE = len(sys.argv) >= 2 and sys.argv[1] == "py2exe"

if PY2EXE:
    try:
        import py2exe
    except ImportError as error:
        print error
        sys.exit(1)

from youtube_dl_gui import (
    __author__,
    __appname__,
    __contact__,
    __version__,
    __license__,
    __projecturl__,
    __description__,
    __packagename__,
    __descriptionfull__
)

# Setup can not handle unicode
__packagename__ = str(__packagename__)


# Helper functions
def create_scripts():
    """Create the binary scripts."""
    dest_dir = os.path.join("build", "_scripts")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    copyfile(os.path.join(__packagename__, "__main__.py"),
             os.path.join(dest_dir, "youtube-dl-gui"))

def build_translations():
    """Build the MO files."""
    exec_name = "msgfmt.exe" if os.name == "nt" else "msgfmt"

    search_pattern = os.path.join("youtube_dl_gui", "locale", "*", "LC_MESSAGES", "*.po")

    for po_file in glob.glob(search_pattern):
        mo_file = po_file.replace(".po", ".mo")

        try:
            print "Building MO file for '%s'" % po_file
            call([exec_name, "-o", mo_file, po_file])
        except OSError:
            print "Could not locate file '%s', exiting..." % exec_name
            sys.exit(1)

##################################


def linux_setup():
    scripts = []
    data_files = []
    package_data = {}

    # Add hicolor icons
    for path in glob.glob("youtube_dl_gui/data/icons/hicolor/*x*"):
        size = os.path.basename(path)

        dst = "share/icons/hicolor/{size}/apps".format(size=size)
        src = "{icon_path}/apps/youtube-dl-gui.png".format(icon_path=path)

        data_files.append((dst, [src]))

    # Add fallback icon, see issue #14
    data_files.append(
        ("share/pixmaps", ["youtube_dl_gui/data/pixmaps/youtube-dl-gui.png"])
    )

    # Add other package data
    package_data[__packagename__] = [
        "data/pixmaps/*.png",
        "data/pixmaps/*.ico",
        "locale/*/LC_MESSAGES/*.mo"
    ]

    # Add scripts
    scripts.append("build/_scripts/youtube-dl-gui")

    setup_params = {
        "scripts": scripts,
        "data_files": data_files,
        "package_data": package_data
    }

    return setup_params


def windows_setup():
    def normal_setup():
        package_data = {}

        # On Windows we dont use the icons under hicolor
        package_data[__packagename__] = [
            "data\\pixmaps\\*.png",
            "data\\pixmaps\\*.ico",
            "locale\\*\\LC_MESSAGES\\*.mo"
        ]

        setup_params = {
            "package_data": package_data
        }

        return setup_params

    def py2exe_setup():
        windows = []
        data_files = []

        # Py2exe dependencies & options
        dependencies = [
            "C:\\Windows\\System32\\ffmpeg.exe",
            "C:\\Windows\\System32\\ffprobe.exe",
            "C:\\python27\\DLLs\\MSVCP90.dll"
        ]

        options = {
            "includes": ["wx.lib.pubsub.*",
                         "wx.lib.pubsub.core.*",
                         "wx.lib.pubsub.core.arg1.*"]
        }
        #############################################

        # Add package data
        data_files.extend([
            ("", dependencies),
            ("data\\pixmaps", glob.glob("youtube_dl_gui\\data\\pixmaps\\*.*")),
        ])

        # We have to manually add the translation files since py2exe cant do it
        for lang in os.listdir("youtube_dl_gui\\locale"):
            dst = os.path.join("locale", lang, "LC_MESSAGES")
            src = os.path.join("youtube_dl_gui", dst, "youtube_dl_gui.mo")

            data_files.append((dst, [src]))

        # Add GUI executable details
        windows.append({
            "script": "build\\_scripts\\youtube-dl-gui",
            "icon_resources": [(0, "youtube_dl_gui\\data\\pixmaps\\youtube-dl-gui.ico")]
        })

        setup_params = {
            "windows": windows,
            "data_files": data_files,
            "options": {"py2exe": options}
        }

        return setup_params

    if PY2EXE:
        return py2exe_setup()

    return normal_setup()


# Execute pre-build stuff
create_scripts()
build_translations()

if os.name == "nt":
    params = windows_setup()
else:
    params = linux_setup()


setup(
    author              = __author__,
    name                = __appname__,
    version             = __version__,
    license             = __license__,
    author_email        = __contact__,
    url                 = __projecturl__,
    description         = __description__,
    long_description    = __descriptionfull__,
    packages            = [__packagename__],

    **params
)
