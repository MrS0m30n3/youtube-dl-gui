#!/bin/bash

# Author: Sotiris Papadopoulos <ytubedlg@gmail.com>
# Last-Updated: 2015-07-02
# Script to update all locale files and rebuild the mo files.

# Usage: ./update_locales.sh


cd ../youtube_dl_gui/

echo "[*]Creating new .PO file"
pygettext.py -v -o new.po *.py

#vim new.po

version=$(grep version version.py | cut -d"'" -f2)
dirs=$(find locale -mindepth 2 -maxdepth 2)

echo "[*]Updating old .PO files"

for dir in $dirs; do
    msgmerge --update --no-wrap -v "$dir/youtube_dl_gui.po" new.po

    # Strip empty headers
    sed -i '/: \\n/d' "$dir/youtube_dl_gui.po"

    # Upate version
    sed -i "s/Project-Id-Version:.*\\\n/Project-Id-Version: youtube-dlg $version\\\n/g" "$dir/youtube_dl_gui.po"
done

echo ""
read -p "Open files for revision?(y/n) " ch

if [ $ch = 'y' ]; then
    for dir in $dirs; do
        vim "$dir/youtube_dl_gui.po"
    done
fi

echo "[*]Building .MO files"

for dir in $dirs; do
    msgfmt --output-file "$dir/youtube_dl_gui.mo" "$dir/youtube_dl_gui.po"
done

echo "[*]Done"

