#!/bin/bash

# Author: Sotiris Papadopoulos <ytubedlg@gmail.com>
# Last-Revision: 2017-01-30
# Script to update all locale files and rebuild the MO files
#
# Usage: ./update_locales.sh

PACKAGE="youtube_dl_gui"

PO_FILE="$PACKAGE.po"

MO_FILE="$PACKAGE.mo"


cd ..

VERSION=$(grep version "$PACKAGE/version.py" | cut -d"'" -f2)

DIRS=$(find "$PACKAGE/locale" -mindepth 2 -maxdepth 2)


echo "[*]Creating new .PO file"

pygettext.py -v -o new.po "$PACKAGE/*.py"

#vim new.po

echo "[*]Updating old .PO files"

for dir in $DIRS; do
    msgmerge --update --no-wrap -v "$dir/$PO_FILE" new.po

    # Strip empty headers
    sed -i "/: \\n/d" "$dir/$PO_FILE"

    # Upate version
    sed -i "s/Project-Id-Version:.*\\\n/Project-Id-Version: youtube-dlg $VERSION\\\n/g" "$dir/$PO_FILE"
done

echo
read -p "Open files for revision?(y/n) " ch

if [ $ch = 'y' ]; then
    for dir in $DIRS; do
        vim "$dir/$PO_FILE"
    done
fi

echo "[*]Building .MO files"

for dir in $DIRS; do
    msgfmt --use-fuzzy --output-file "$dir/$MO_FILE" "$dir/$PO_FILE"
done

echo "[*]Done"
