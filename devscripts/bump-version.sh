#!/bin/bash

# Author: Sotiris Papadopoulos <ytubedlg@gmail.com>
# Last-Revision: 2017-04-17
# Script to bump the version and automatically update related files
#
# Usage: ./bump_version.sh <new-version>

PACKAGE="youtube_dl_gui"

FILES=`cat <<EOF
$PACKAGE/version.py
.github/ISSUE_TEMPLATE.md
README.md
youtube-dl-gui.1
EOF`

# Update version string on given file
# $1 = current version
# $2 = new version
# $3 = file
function update_version {
    echo "Updating file: $3"
    sed -i "s/$1/$2/g" $3
}

# Returns 'true' if given version is less or equal to the current version
# $1 = version to check
# $2 = current version
function version_le {
    smallest_version=`echo -e "$1\n$2" | sort -V | head -n1`
    [ "$1" = "$smallest_version" ]
}


if [ $# -ne 1 ]; then
    echo "Usage ./bump_version.sh <new-version>"
    exit 1
fi

cd ..

new_version=$1
cur_version=`grep version "$PACKAGE/version.py" | cut -d"'" -f2`

echo "Current version = $cur_version"
echo "New version     = $new_version"
echo

if version_le $new_version $cur_version; then
    echo "New version must be greater than the current version, exiting..."
    exit 1
fi

for file in $FILES; do
    update_version $cur_version $new_version $file
done

echo "Done"
