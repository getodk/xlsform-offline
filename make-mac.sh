#!/bin/bash
set -e

VERSION=$(grep Version src/res/about.html | sed -e 's|[[:space:]]*\(Version:\)[[:space:]]*\(.*\)$|\2|');
BINARY='dist/mac/ODK XLSForm Offline.app';

cd "$XLSFORM";

echo "Removing build and dist";
rm -rf build/xlsform-offline-mac; 
rm -rf dist/mac;
find . -name '*.pyc' -type f -delete;

echo "Creating new build";
pyinstaller pkg/xlsform-offline-mac.spec --distpath ../dist/mac  --onefile --windowed --noconfirm --clean;

if [[ -e "$BINARY" ]]; then
	echo 'Adding version info';
	cd "$BINARY/Contents";
	sed -i -e "s/0.0.0/$VERSION/" Info.plist;
fi