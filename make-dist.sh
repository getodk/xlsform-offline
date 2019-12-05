#!/bin/bash
set -e

README='pkg/Read me.txt'

MAC_BINARY='dist/mac/ODK XLSForm Offline.app'
MAC_README='dist/mac/Read me.txt'

if [[ -e "$MAC_BINARY" ]]; then
	echo 'Mac version exists';
	fold -w 80 -s "$README" > "$MAC_README";
	cd dist/mac;
	zip -r9 "ODK-XLSForm-Offline-macOS.zip" . -x "*.DS_Store"
	cd ../..;
fi