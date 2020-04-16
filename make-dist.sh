  
#!/bin/bash
set -e

VERSION=$(git describe --tags --dirty --always)

README='pkg/Read me.txt'

CWD=$(pwd)

MAC_BINARY="dist/mac/ODK-XLSForm-Offline.app"
MAC_README="dist/mac/Read me.txt"

# Travis workspaces is weird with windows
WIN_DIR="C:${CWD}/dist/win"
WIN_BINARY="${WIN_DIR}/ODK-XLSForm-Offline.exe"
WIN_README="${WIN_DIR}/Read me.txt"

if [[ -e "$MAC_BINARY" ]]; then
	echo 'Mac version exists';
	fold -w 80 -s "$README" > "$MAC_README";
	cd dist/mac;
	mv "ODK-XLSForm-Offline.app" "ODK XLSForm Offline.app" 
	# Add the binary version in the zip name
	zip -r9 "ODK-XLSForm-Offline-macOS-${VERSION}.zip" . -x "*.DS_Store"
	echo "ODK-XLSForm-Offline-macOS-${VERSION}.zip"
	cd $CWD;
fi

if [[ -e "$WIN_BINARY" ]]; then
	if ! [[ -d dist ]]; then
		mkdir dist
	fi
	mkdir dist/win
	echo 'Windows version exists';
	fold -w 80 -s "$README" > "$WIN_README";
	mac2unix "$WIN_README" && unix2dos "$WIN_README";
	cd $WIN_DIR;
	ls
	mv "ODK-XLSForm-Offline.exe" "ODK XLSForm Offline.exe"
	zip -r9 "ODK-XLSForm-Offline-Windows.zip" . -x "*.DS_Store"
	# Add the binary version in the zip name
	mv "ODK-XLSForm-Offline-Windows.zip" "$CWD/dist/win/ODK-XLSForm-Offline-Windows-${VERSION}.zip"
	echo "$CWD/dist/win/ODK-XLSForm-Offline-Windows-${VERSION}.zip"
	cd $CWD;
fi