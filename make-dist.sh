#!/bin/bash
set -e

VERSION=$(grep Version src/res/about.html | sed -e 's|[[:space:]]*\(Version:\)[[:space:]]*\(.*\)$|\2|');

README='pkg/Read me.txt'

MAC_BINARY='dist/mac/ODK XLSForm Offline.app'
MAC_README='dist/mac/Read me.txt'

WIN_BINARY='dist/win/ODK XLSForm Offline.exe'
WIN_README='dist/win/Read me.txt'

if [[ -e "$MAC_BINARY" ]]; then
	echo 'Mac version exists';
	fold -w 80 -s "$README" > "$MAC_README";
	cd dist/mac;
	zip -r9 "ODK-XLSForm-Offline-Mac-$VERSION.zip" . -x "*.DS_Store"
	cd ../..;
fi

if [[ -e "$WIN_BINARY" ]]; then
	echo 'Windows version exists';
	fold -w 80 -s "$README" > "$WIN_README";
	mac2unix "$WIN_README" && unix2dos "$WIN_README";
	cd dist/win;
	zip -r9 "ODK-XLSForm-Offline-Win-$VERSION.zip" . -x "*.DS_Store"
	cd ../..;
fi