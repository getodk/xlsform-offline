# ODK XLSForm Offline
![Platform](https://img.shields.io/badge/platform-Python-blue.svg)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Slack status](http://slack.opendatakit.org/badge.svg)](http://slack.opendatakit.org)
![Build status](https://travis-ci.com/opendatakit/xlsform-offline.svg?branch=master)

ODK XLSForm Offline is a Windows and macOS application for converting an XLSForm into an XForm that is compliant with the [ODK XForms spec](http://opendatakit.github.io/xforms-spec). Once converted, the application also validates that the XForm will run perfectly with all ODK tools.
   
ODK XLSForm Offline is part of Open Data Kit (ODK), a free and open-source set of tools which help organizations author, field, and manage mobile data collection solutions. Learn more about the Open Data Kit project and its history [here](https://opendatakit.org/about/) and read about example ODK deployments [here](https://opendatakit.org/about/deployments/).

* ODK website: [https://opendatakit.org](https://opendatakit.org)
* ODK forum: [https://forum.opendatakit.org](https://forum.opendatakit.org)
* ODK developer Slack chat: [http://slack.opendatakit.org](http://slack.opendatakit.org) 
* ODK developer Slack archive: [http://opendatakit.slackarchive.io](http://opendatakit.slackarchive.io) 
* ODK developer wiki: [https://github.com/opendatakit/opendatakit/wiki](https://github.com/opendatakit/opendatakit/wiki)

## Prerequisites

1. Install [Python 2.7](https://www.python.org/downloads/)
	* Windows: Use the 32 bit version.
1. Install Python packages: ``pip install pyinstaller wxpython pyxform``
	* macOS: Use the default Python. virtualenvs will not work.
1. Install packaging utilities
	* macOS: ``brew install unix2dos``
	* Windows: [upx](https://upx.github.io/)

## Run

To run the app, `python src/main.py`

## Package

The easiest way to package is to use a macOS machine running a Windows 10 virtual machine and a macOS virtual machine. Both VMs should have Python installed natively (no virtualenv, no pyenv) to minimize problems with pyinstaller.

1. In the macOS VM, run `./make-mac.sh` to build the Mac binary.
1. In the Windows VM, run `make-win.bat` to build the Windows binary.
1. Copy the resulting binaries into the `dist/mac` and `dist/win` folders on the host machine.
1. On the host machine, run `./make-dist.sh` to zip up the Mac and Windows binaries.
