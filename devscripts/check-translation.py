#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author: Sotiris Papadopoulos <ytubedlg@gmail.com>
Last-Revision: 2017-04-19

Script to automatically check PO files

"""

from __future__ import unicode_literals

import os
import sys
import logging
import argparse

from time import sleep
from datetime import datetime, timedelta, tzinfo

try:
    import polib
    import google_translate
except ImportError as error:
    print(error)
    sys.exit(1)


WTIME = 2.0  # Time in seconds to wait between requests to avoid ban

PACKAGE = "youtube_dl_gui"

PO_FILENAME = "{}.po".format(PACKAGE)

LOCALE_PATH_TMPL = os.path.join(PACKAGE, "locale", "{lang}", "LC_MESSAGES", PO_FILENAME)


logging.basicConfig(level=logging.ERROR)


def parse():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Script to automatically check PO files")

    parser.add_argument("language", help="language of the PO file to check")

    parser.add_argument("-w", "--werror", action="store_true", help="treat all warning messages as errors")
    parser.add_argument("-o", "--only-headers", action="store_true", help="check only the PO file headers")
    parser.add_argument("-n", "--no-translate", action="store_true", help="do not use the translator to check 'msgstr' fields")

    return parser.parse_args()


class UTC_Offset_Timezone(tzinfo):

    """Class that represents a UTC offset in the format +/-0000."""

    def __init__(self, offset_string):
        self.offset = timedelta(seconds=UTC_Offset_Timezone.parse_offset(offset_string))

    def utcoffset(self, dt):
        return self.offset + self.dst(dt)

    def dst(self, dt):
        return timedelta(0)

    @staticmethod
    def parse_offset(offset_string):
        """Parse the offset string into seconds."""

        if len(offset_string) != 5:
            raise ValueError("Invalid length for offset string ({})".format(offset_string))

        hours = offset_string[1:3]
        minutes = offset_string[3:5]

        offset = int(hours) * 3600 + int(minutes) * 60

        if offset_string[0] == "-":
            return -1 * offset

        return offset


def parse_date(date_string):
    """Parse date string into an aware datetime object."""

    # Just a small list with the most common timezones
    offset_list = [
        ("EEST", "0300"),
        ("EET", "0200"),
        ("GMT", "0000"),
        ("UTC", "0000")
    ]

    # Replace all the timezones with the offset
    for item in offset_list:
        timezone, offset = item

        date_string = date_string.replace(timezone, offset)

    datetime_string = date_string[:16]
    offset_string = date_string[16:]

    naive_date = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M")

    # Create & return an aware datetime object based on the offset
    return naive_date.replace(tzinfo=UTC_Offset_Timezone(offset_string))

# Print helpers

def my_print(msg, char="*", value=None, exit=False):
    """Print 'msg', debug 'value' and exit if 'exit' is True."""
    print("[{}] {}".format(char, msg))

    if value is not None:
        print("\tvalue= \"{}\"".format(value))

    if exit:
        sys.exit(1)

def perror(msg, value=None):
    my_print(msg, "-", value, True)

def pwarn(msg, value=None, exit=False):
    my_print(msg, "!", value, exit)

def pinfo(msg):
    my_print(msg)

#############################


def main(args):
    os.chdir("..")

    # setup
    pot_file_path = LOCALE_PATH_TMPL.format(lang="en_US")
    po_file_path = LOCALE_PATH_TMPL.format(lang=args.language)

    if not os.path.exists(pot_file_path):
        perror("Failed to locate POT file, exiting...", pot_file_path)

    if not os.path.exists(po_file_path):
        perror("Failed to locate PO file, exiting...", po_file_path)

    pot_file = polib.pofile(pot_file_path)
    po_file = polib.pofile(po_file_path)

    # check headers
    pinfo("Checking PO headers")

    pot_headers = pot_file.metadata
    po_headers = po_file.metadata

    if pot_headers["Project-Id-Version"] != po_headers["Project-Id-Version"]:
        pwarn("'Project-Id-Version' headers do not match", exit=args.werror)

    if pot_headers["POT-Creation-Date"] != po_headers["POT-Creation-Date"]:
        pwarn("'POT-Creation-Date' headers do not match", exit=args.werror)

    po_creation_date = parse_date(po_headers["POT-Creation-Date"])
    po_revision_date = parse_date(po_headers["PO-Revision-Date"])

    # Aware datetimes convert to UTC automatically when comparing
    if po_revision_date <= po_creation_date:
        pwarn("PO file seems outdated", exit=args.werror)

    if "Language" in po_headers and po_headers["Language"] != args.language:
        pwarn("'Language' header does not match with the given language", po_headers["Language"], args.werror)

    pinfo("Last-Translator: {}".format(po_headers["Last-Translator"]))

    # check translations
    if args.only_headers:
        sys.exit(0)

    pinfo("Checking translations, this might take a while...")

    eta = timedelta(seconds=len(pot_file) * WTIME)

    pinfo("Approximate time to check translations online: {}".format(eta))

    pot_msgid = [entry.msgid for entry in pot_file]
    po_msgid = [entry.msgid for entry in po_file]

    # lists to hold reports
    missing_msgid = []
    not_translated = []
    same_msgstr = []
    with_typo = []
    verify_trans = []
    fuzzy_trans = po_file.fuzzy_entries()

    for msgid in pot_msgid:
        if msgid not in po_msgid:
            missing_msgid.append(msgid)

    translator = google_translate.GoogleTranslator(timeout=5.0, retries=2, wait_time=WTIME)

    # Get a valid source language for Google
    # for example convert 'ar_SA' to 'ar' or 'zh_CN' to 'zh-CN'
    src_lang = args.language

    if src_lang not in translator._lang_dict:
        src_lang = src_lang.replace("_", "-")

        if src_lang not in translator._lang_dict:
            src_lang = src_lang.split("-")[0]

    for entry in po_file:
        if not entry.translated():
            not_translated.append(entry)

        elif entry.msgid == entry.msgstr:
            same_msgstr.append(entry)

        else:
            if args.no_translate:
                continue

            word_dict = translator.get_info_dict(entry.msgstr, "en", src_lang)

            if word_dict is not None:
                if word_dict["has_typo"]:
                    with_typo.append(entry)

                if word_dict["translation"].lower() != entry.msgid.lower():

                    found = False

                    # Check verbs, nouns, adverbs, etc..
                    for key in word_dict["extra"]:
                        if entry.msgid.lower() in word_dict["extra"][key].keys():
                            found = True
                            break

                    if not found:
                        verify_trans.append((entry, word_dict["translation"]))

            sleep(WTIME)

    # time to report
    print("=" * 25 + "Report" + "=" * 25)

    if missing_msgid:
        print("Missing msgids")

        for msgid in missing_msgid:
            print("  \"{}\"".format(msgid))

    if not_translated:
        print("Not translated")

        for entry in not_translated:
            print("  line: {} msgid: \"{}\"".format(entry.linenum, entry.msgid))

    if same_msgstr:
        print("Same msgstr")

        for entry in same_msgstr:
            print("  line: {} msgid: \"{}\"".format(entry.linenum, entry.msgid))

    if with_typo:
        print("With typo")

        for entry in with_typo:
            print("  line: {} msgid: \"{}\" msgstr: \"{}\"".format(entry.linenum, entry.msgid, entry.msgstr))

    if verify_trans:
        print("Verify translation")

        for item in verify_trans:
            entry, translation = item
            print("  line: {} msgid: \"{}\" trans: \"{}\"".format(entry.linenum, entry.msgid, translation))

    if fuzzy_trans:
        print("Fuzzy translations")

        for entry in fuzzy_trans:
            print("  line: {} msgid: \"{}\"".format(entry.linenum, entry.msgid))

    total = len(missing_msgid) + len(not_translated) + len(same_msgstr) + len(with_typo) + len(verify_trans) + len(fuzzy_trans)

    print("")
    print("Missing msgids\t\t: {}".format(len(missing_msgid)))
    print("Not translated\t\t: {}".format(len(not_translated)))
    print("Same msgstr\t\t: {}".format(len(same_msgstr)))
    print("With typo\t\t: {}".format(len(with_typo)))
    print("Verify translation\t: {}".format(len(verify_trans)))
    print("Fuzzy translations\t: {}".format(len(fuzzy_trans)))
    print("Total\t\t\t: {}".format(total))


if __name__ == "__main__":
    try:
        main(parse())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
