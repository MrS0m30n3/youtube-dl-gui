#!/usr/bin/env python

"""
Author: Sotiris Papadopoulos <ytubedlg@gmail.com>
Last-Revision: 2017-01-30

Script to add support for a new language

Usage   : ./new-locale.py <language_code>
Example : ./new-locale.py en_US

"""

import os
import sys
import shutil


PACKAGE = "youtube_dl_gui"

LOCALE_PATH_TMPL = os.path.join(PACKAGE, "locale", "{lang}", "LC_MESSAGES")

PO_FILE_TMPL = os.path.join("{parent_dir}", "youtube_dl_gui.po")


def error(msg):
    print("[-]{0}".format(msg))
    sys.exit(1)


def output(msg):
    print("[*]{0}".format(msg))


def manage_directory():
    """Allow script calls from the 'devscripts' dir and the package dir."""
    if os.path.basename(os.getcwd()) == "devscripts":
        os.chdir("..")


def main(lang_code):
    manage_directory()

    target_dir = LOCALE_PATH_TMPL.format(lang=lang_code)
    default_dir = LOCALE_PATH_TMPL.format(lang="en_US")

    target_po = PO_FILE_TMPL.format(parent_dir=target_dir)
    source_po = PO_FILE_TMPL.format(parent_dir=default_dir)

    if os.path.exists(target_dir):
        error("Locale '{0}' already exists, exiting...".format(lang_code))

    output("Creating directory: '{0}'".format(target_dir))
    os.makedirs(target_dir)

    output("Creating PO file: '{0}'".format(target_po))
    shutil.copy(source_po, target_po)

    output("Done")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Usage   : {0} <language_code>".format(sys.argv[0]))
        print("Example : {0} en_US".format(sys.argv[0]))
