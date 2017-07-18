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

        python setup.py build_trans

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
            * Set up package level pixmaps icons (*.png)
            * Set up package level i18n files (*.mo)
            * Set up scripts (executables) (if supported by platform)
        * Run setup

"""

from distutils import cmd
from distutils.core import setup
from distutils.command.build import build

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
        print(error)
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


def on_windows():
    """Returns True if OS is Windows."""
    return os.name == "nt"


class BuildBin(cmd.Command):

    description = "build the youtube-dl-gui binary file"
    user_options = []

    def initialize_options(self):
        self.scripts_dir = None

    def finalize_options(self):
        self.scripts_dir = os.path.join("build", "_scripts")

    def run(self):
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir)

        copyfile(os.path.join(__packagename__, "__main__.py"),
                 os.path.join(self.scripts_dir, "youtube-dl-gui"))


class BuildTranslations(cmd.Command):

    description = "build the translation files"
    user_options = []

    def initialize_options(self):
        self.exec_name = None
        self.search_pattern = None

    def finalize_options(self):
        if on_windows():
            self.exec_name = "msgfmt.exe"
        else:
            self.exec_name = "msgfmt"

        self.search_pattern = os.path.join(__packagename__, "locale", "*", "LC_MESSAGES", "youtube_dl_gui.po")

    def run(self):
        for po_file in glob.glob(self.search_pattern):
            mo_file = po_file.replace(".po", ".mo")

            try:
                print("building MO file for '{}'").format(po_file)
                call([self.exec_name, "-o", mo_file, po_file])
            except OSError:
                print("could not locate file '{}', exiting...".format(self.exec_name))
                sys.exit(1)


class Build(build):

    """Overwrite the default 'build' behaviour."""

    sub_commands = [
        ("build_bin", None),
        ("build_trans", None)
    ] + build.sub_commands

    def run(self):
        build.run(self)


# Overwrite cmds
cmdclass = {
    "build": Build,
    "build_bin": BuildBin,
    "build_trans": BuildTranslations
}


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

    # Add pixmaps icons (*.png) & i18n files
    package_data[__packagename__] = [
        "data/pixmaps/*.png",
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

        # Add pixmaps icons (*.png) & i18n files
        package_data[__packagename__] = [
            "data\\pixmaps\\*.png",
            "locale\\*\\LC_MESSAGES\\*.mo"
        ]

        setup_params = {
            "package_data": package_data
        }

        return setup_params

    def py2exe_setup():
        windows = []
        data_files = []

        # py2exe dependencies & options
        # TODO change directory for ffmpeg.exe & ffprobe.exe
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

        # Add py2exe deps & pixmaps icons (*.png)
        data_files.extend([
            ("", dependencies),
            ("data\\pixmaps", glob.glob("youtube_dl_gui\\data\\pixmaps\\*.png")),
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


if on_windows():
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
    cmdclass            = cmdclass,

    **params
)
