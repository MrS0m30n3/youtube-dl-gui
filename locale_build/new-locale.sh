#!/bin/bash

# Author: Sotiris Papadopoulos <ytubedlg@gmail.com>
# Last-Revision: 2017-01-30
# Script to add support for a new language
#
# Usage: ./new-locale.sh <locale>
# Example: ./new-locale.sh gr_GR

PACKAGE="youtube_dl_gui"

PO_FILE="$PACKAGE.po"


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <locale>"
    echo "Example: $0 gr_GR"
    exit 1
fi

cd ..

TARGET="$PACKAGE/locale/$1"


if [ -d "$TARGET" ]; then
    echo "[-]Locale '$1' already exists, exiting..."
    exit 1
fi

echo "[*]Creating directory: '$TARGET'"
mkdir -p "$TARGET/LC_MESSAGES"

echo "[*]Copying files..."
cp -v "$PACKAGE/locale/en_US/LC_MESSAGES/$PO_FILE" "$TARGET/LC_MESSAGES/$PO_FILE"

echo "[*]Done"
