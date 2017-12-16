# ODK XLSForm Offline
![Platform](https://img.shields.io/badge/platform-Python-blue.svg)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Slack status](http://slack.opendatakit.org/badge.svg)](http://slack.opendatakit.org)

ODK XLSForm Offline is a Python application for converting an XLSForm into an XForm that is compliant with the [ODK XForms spec](http://opendatakit.github.io/xforms-spec). It runs on macOS and Windows.
   
ODK XLSForm Offline is part of Open Data Kit (ODK), a free and open-source set of tools which help organizations author, field, and manage mobile data collection solutions. Learn more about the Open Data Kit project and its history [here](https://opendatakit.org/about/) and read about example ODK deployments [here](https://opendatakit.org/about/deployments/).

* ODK website: [https://opendatakit.org](https://opendatakit.org)
* ODK forum: [https://forum.opendatakit.org](https://forum.opendatakit.org)
* ODK developer Slack chat: [http://slack.opendatakit.org](http://slack.opendatakit.org) 
* ODK developer Slack archive: [http://opendatakit.slackarchive.io](http://opendatakit.slackarchive.io) 
* ODK developer wiki: [https://github.com/opendatakit/opendatakit/wiki](https://github.com/opendatakit/opendatakit/wiki)

## Prerequisites

1. Install [Python 2.7](https://www.python.org/downloads/)
	* If you are on Windows, you must install the 32 bit version.
1. Install Python packages: ``pip install pyinstaller wxpython pyxform``
1. Until [pyxform/pull/166](https://github.com/XLSForm/pyxform/pull/166) is merged, uninstall the official version of pyxform, and install a branch that works with PyInstaller.
	* Uninstall offical: ``pip uninstall pyxform -y``
	* Install PyInstaller branch: ``pip install git+https://github.com/yanokwa/pyxform.git@pyinstaller-windows``
1. Install utilities
	* macOS: ``brew install unix2dos``
	* Windows: [upx](https://upx.github.io/)

## Running

To run the app, `python src/main.py`

##  Packaging

We package on macOS machine running a Windows 10 virtual machine. We share the `xlsform-offline` folder on the Mac with Windows, then mount that folder as the Z drive with `pushd "\\vmware-host\Shared Folders\xlsform-offline\"`.

1. On macOS, run `./make-mac.sh`
1. On Windows, run `make-win.bat`
1. On macOS, run `./make-dist.sh`
