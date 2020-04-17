#!/bin/bash
set -e

BINARY='dist/mac/ODK XLSForm Offline.app';

echo "Removing build and dist";
rm -rf build/xlsform-offline-mac; 
rm -rf dist/mac;
find . -name '*.pyc' -type f -delete;

echo "Creating new build";
pyinstaller pkg/xlsform-offline-mac.spec --distpath $(pwd)/dist/mac  --onefile --windowed --noconfirm --clean;
