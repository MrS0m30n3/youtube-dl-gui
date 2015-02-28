#!/bin/bash

# Author: Sotiris Papadopoulos
# Last-Edited: 25/02/2015
# Script to auto-create a locale file.

# Usage: ./build_locale.sh <locale> <locale_file>
# Example: ./build_locale.sh gr_GR gr.po

# To create a new locale file copy youtube_dl_gui.po
# to a new locale file (e.g. gr.po) edit it with your
# favorite editor and then run this script.


FILENAME="youtube_dl_gui"

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <locale> <locale_file>"
	echo "Example: $0 gr_GR gr.po"
	exit 1
fi

mkdir -p "../$FILENAME/locale/$1/LC_MESSAGES/"

msgfmt --output-file "$FILENAME.mo" "$2"

mv "$2" "../$FILENAME/locale/$1/LC_MESSAGES/$FILENAME.po"
mv "$FILENAME.mo" "../$FILENAME/locale/$1/LC_MESSAGES/"

tree "../$FILENAME/locale/$1"

echo "Done"
