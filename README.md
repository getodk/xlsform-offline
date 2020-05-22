# ODK XLSForm Offline
![Platform](https://img.shields.io/badge/platform-Python-blue.svg)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build status](https://api.travis-ci.org/getodk/xlsform-offline.svg?branch=master)](https://travis-ci.org/github/getodk/xlsform-offline)
[![Slack](https://img.shields.io/badge/chat-on%20slack-brightgreen)](https://slack.getodk.org)

ODK XLSForm Offline is a Windows and macOS application for converting an XLSForm into an XForm that is compliant with the [ODK XForms spec](http://getodk.github.io/xforms-spec). Once converted, the application also validates that the XForm will run perfectly with all ODK tools.
   
ODK XLSForm Offline is part of ODK, a free and open-source set of tools which help organizations author, field, and manage mobile data collection solutions. Learn more about the ODK project and its history [here](https://getodk.org/about/) and read about example ODK deployments [here](https://getodk.org/about/deployments/).

* ODK website: [https://getodk.org](https://getodk.org)
* ODK forum: [https://forum.getodk.org](https://forum.getodk.org)
* ODK developer Slack chat: [https://slack.getodk.org](https://slack.getodk.org)

## Prerequisites

1. Install [Python 3.6](https://www.python.org/downloads/)
	* Windows: Use the 32 bit version.
1. Install Python packages: ``pip3 install -r requirements.txt``
	* macOS: Use the default Python. virtualenvs will not work.
1. Install packaging utilities
	* macOS: ``brew install unix2dos upx``
	* Windows: [upx](https://upx.github.io/)

## Run

To run the app, `python src/main.py`

## Automated packaging

[Travis](https://travis-ci.com/) will automatically build all of this repo's branches and place the binaries here for 30 days.

* Mac: https://travis.getodk.org/xlsform-offline/ODK-XLSForm-Offline-macOS-{GIT_HASH}.zip
* Windows: https://travis.getodk.org/xlsform-offline/ODK-XLSForm-Offline-Windows-{GIT_HASH}.zip

`{GIT_HASH}` should be replaced with the output of the command:
```shell 
git describe --tags --dirty --always
```

## Manual packaging

The easiest way to do manual packaging is to use a macOS machine running a Windows 10 virtual machine and a macOS virtual machine. Both VMs should have Python installed natively (no virtualenv, no pyenv) to minimize problems with pyinstaller.

1. In the macOS VM, run `./make-mac.sh` to build the Mac binary.
1. In the Windows VM, run `make-win.bat` to build the Windows binary.
1. Copy the resulting binaries into the `dist/mac` and `dist/win` folders on the host machine.
1. On the host machine, run `./make-dist.sh` to zip up the Mac and Windows binaries.

## Releases

Before releasing a version, be sure to update the version in src/res/about.html
