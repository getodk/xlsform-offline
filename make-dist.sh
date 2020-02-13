#!/bin/bash
set -e

README='pkg/Read me.txt'

MAC_BINARY='dist/mac/ODK XLSForm Offline.app'
MAC_README='dist/mac/Read me.txt'

VERSION=$(grep VERSION src/main.py | sed -e "s|.*'\(.*\)'|\1|")

if [[ -e "$MAC_BINARY" ]]; then
	echo 'Mac version exists';
	fold -w 80 -s "$README" > "$MAC_README";
	cd dist/mac;
	zip -r9 "ODK-XLSForm-Offline-macOS-$VERSION.zip" . -x "*.DS_Store"
	cd ../..;
fi