# -*- coding: utf-8 -*-

"""Youtube-dlg setup file.

Examples:
    Windows/Linux::

        python setup.py pyinstaller

    Linux::

        python setup.py install

    Build source distribution::

        python setup.py sdist

    Build platform distribution::

        python setup.py bdist

    Build the translations::

        python setup.py build_trans

    Build with updates disabled::

        python setup.py no_updates


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

import glob
import os
import sys
from setuptools import setup, Command
from distutils import log
from distutils.spawn import spawn
from distutils.errors import DistutilsExecError
import time

import polib


__author__ = 'Sotiris Papadopoulos'
__contact__ = 'ytubedlg@gmail.com'
__maintainer__ = 'Oleksis Fraga'
__maintainer_contact__ = 'oleksis.fraga@gmail.com'
__projecturl__ = 'https://github.com/oleksis/youtube-dl-gui/'
__appname__ = 'Youtube-DLG'
__license__ = 'UNLICENSE'
__description__ = 'Youtube-dl GUI'
__descriptionfull__ = '''A cross platform front-end GUI of the popular
youtube-dl written in wxPython Phoenix'''
__licensefull__ = '''
This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>'''
__packagename__ = "youtube_dl_gui"
DESCRIPTION = __description__
LONG_DESCRIPTION = __descriptionfull__

PYINSTALLER = len(sys.argv) >= 2 and sys.argv[1] == "pyinstaller"

try:
    from PyInstaller import compat as pyi_compat

    if pyi_compat.is_win:
        # noinspection PyUnresolvedReferences
        from PyInstaller.utils.win32.versioninfo import (
            VarStruct, VarFileInfo, StringStruct, StringTable,
            StringFileInfo, FixedFileInfo, VSVersionInfo, SetVersion,
        )
except ImportError:
    pyi_compat = None
    if PYINSTALLER:
        print("Cannot import pyinstaller", file=sys.stderr)
        exit(1)

# Get the version from youtube_dl_gui/version.py without importing the package
exec(compile(open(__packagename__+"/version.py").read(), __packagename__+"/version.py", "exec"))


def on_windows():
    """Returns True if OS is Windows."""
    return os.name == "nt"


def version2tuple(commit=0):
    version_list = str(__version__).split(".")
    if len(version_list) > 3:
        _commit = int(version_list[3])
        del version_list[3]
    else:
        _commit = commit

    _year, _month, _day = [int(value) for value in version_list]
    return _year, _month, _day, _commit


def version2str(commit=0):
    version_tuple = version2tuple(commit)
    return "%s.%s.%s.%s" % version_tuple


# noinspection PyAttributeOutsideInit,PyArgumentList
class BuildTranslations(Command):
    description = "Build the translation files"
    user_options = []

    def initialize_options(self):
        self.search_pattern = None

    def finalize_options(self):
        self.search_pattern = os.path.join(__packagename__, "locale", "*", "LC_MESSAGES", "youtube_dl_gui.po")

    def run(self):
        tools_path = os.path.join(sys.exec_prefix, 'bin')
        msgfmt_file = os.path.join(tools_path, 'msgfmt')

        try:
            for po_file in glob.glob(self.search_pattern):
                mo_file = po_file.replace('.po', '.mo')
                po = polib.pofile(po_file)

                log.info("Building MO file for '{}'".format(po_file))
                po.save_as_mofile(mo_file)
        except:
            log.error("Could not locate file '{}', exiting...".format(po_file))
            sys.exit(1)


# noinspection PyAttributeOutsideInit,PyArgumentList
class BuildNoUpdate(Command):
    description = "Build with updates disabled"
    user_options = []

    def initialize_options(self):
        self.build_lib = os.path.dirname(os.path.abspath(__file__))

    def finalize_options(self):
        pass

    def run(self):
        self.__disable_updates()

    def __disable_updates(self):
        lib_dir = os.path.join(self.build_lib, __packagename__)
        target_file = "optionsmanager.py"
        # Options file should be available from previous build commands
        optionsfile = os.path.join(lib_dir, target_file)

        with open(optionsfile, "r") as input_file:
            data = input_file.readlines()

        if data is None:
            log.error("Building with updates disabled failed!")
            sys.exit(1)

        for index, line in enumerate(data):
            if "'disable_update': False" in line:
                log.info("Disabling updates...")
                data[index] = line.replace("False", "True")
                break

        with open(optionsfile, "w") as output_file:
            output_file.writelines(data)


class BuildPyinstallerBin(Command):
    description = "Build the executable"
    user_options = []
    version_file = None
    if pyi_compat and pyi_compat.is_win:
        version_file = VSVersionInfo(
            ffi=FixedFileInfo(
                filevers=version2tuple(),
                prodvers=version2tuple(),
                mask=0x3F,
                flags=0x0,
                OS=0x4,
                fileType=0x1,
                subtype=0x0,
                date=(0, 0),
            ),
            kids=[
                VarFileInfo([VarStruct("Translation", [0, 1200])]),
                StringFileInfo(
                    [
                        StringTable(
                            "000004b0",
                            [
                                StringStruct("CompanyName", "oleksis.fraga@gmail.com"),
                                StringStruct("FileDescription", DESCRIPTION),
                                StringStruct("FileVersion", version2str()),
                                StringStruct("InternalName", "youtube-dl-gui.exe"),
                                StringStruct(
                                    "LegalCopyright",
                                    __projecturl__ + "LICENSE",
                                ),
                                StringStruct("OriginalFilename", "youtube-dl-gui.exe"),
                                StringStruct("ProductName", __appname__),
                                StringStruct("ProductVersion", version2str()),
                            ],
                        )
                    ]
                ),
            ],
        )

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self, version=version_file):
        #  --add-data <SRC;DEST or SRC:DEST>
        # ``os.pathsep`` which is ``;`` on Windows
        # and ``:`` on most unix systems) is used.
        if on_windows():
            path_sep = ";"
        else:
            path_sep = ":"
        
        spawn(
            [
                "pyinstaller",
                "-w",
                "-F",
                "--icon="+__packagename__+"/data/pixmaps/youtube-dl-gui.ico",
                "--add-data="+__packagename__+"/data"+path_sep+__packagename__+"/data",
                "--add-data="+__packagename__+"/locale"+path_sep+__packagename__+"/locale",
                "--exclude-module=tests",
                "--name=youtube-dl-gui",
                ""+__packagename__+"/__main__.py",
            ],
            dry_run=self.dry_run)

        if version:
            time.sleep(3)
            SetVersion("./dist/youtube-dl-gui.exe", version)


pyinstaller_console = [
    {
        "script": "./"+__packagename__+"/__main__.py",
        "dest_base": __packagename__,
        "version": __version__,
        "description": DESCRIPTION,
        "comments": LONG_DESCRIPTION,
        "product_name": __appname__,
        "product_version": __version__,
    }
]

cmdclass = {
    "build_trans": BuildTranslations,
    "no_updates": BuildNoUpdate,
}


def setup_linux():
    """Setup params for Linux"""
    data_files_linux = []
    # Add hicolor icons
    for path in glob.glob("youtube_dl_gui/data/icons/hicolor/*x*"):
        size = os.path.basename(path)

        dst = "share/icons/hicolor/{size}/apps".format(size=size)
        src = "{icon_path}/apps/youtube-dl-gui.png".format(icon_path=path)

        data_files_linux.append((dst, [src]))
    # Add fallback icon, see issue #14
    data_files_linux.append(
        ("share/pixmaps", ["youtube_dl_gui/data/pixmaps/youtube-dl-gui.png"])
    )
    # Add man page
    data_files_linux.append(
        ("share/man/man1", ["youtube-dl-gui.1"])
    )
    # Add pixmaps icons (*.png) & i18n files
    package_data_linux = {__packagename__: [
        "data/pixmaps/*.png",
        "locale/*/LC_MESSAGES/*.mo"
    ]}
    setup_params = {
        "data_files": data_files_linux,
        "package_data": package_data_linux,
    }

    return setup_params


def setup_windows():
    """Setup params for Windows"""
    package_data_windows = {__packagename__: [
        "data\\pixmaps\\*.png",
        "locale\\*\\LC_MESSAGES\\*.mo"
    ]}
    # Add pixmaps icons (*.png) & i18n files
    setup_params = {
        "package_data": package_data_windows,
    }

    return setup_params


params = dict()

if PYINSTALLER:
    cmdclass.update({"pyinstaller": BuildPyinstallerBin})
else:
    if on_windows():
        params = setup_windows()
    else:
        params = setup_linux()

    params["entry_points"] = {
        "console_scripts": ["youtube-dl-gui = " + __packagename__ + ":main"]
    }


setup(
    name=__packagename__,
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=__projecturl__,
    author=__author__,
    author_email=__contact__,
    maintainer=__maintainer__,
    maintainer_email=__maintainer_contact__,
    license=__license__,
    packages=[__packagename__],
    classifiers=[
        "Topic :: Multimedia :: Video :: User Interfaces",
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X :: Cocoa",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: GTK",
        "License :: Public Domain",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    cmdclass=cmdclass,
    **params
)
