import wx
import sys

import requests
from packaging import version
import threading

GITHUB_RELEASES_API = "https://api.github.com/repos/opendatakit/xlsform-offline/releases/latest"

OS_MAP = {
    'win32': 'windows',
    'darwin': 'macos'
}

EVT_UPDATE_CHECKER = wx.NewId()


def evt_update_check_done(win, func):
    '''Define Update Check Done Event.'''
    win.Connect(-1, -1, EVT_UPDATE_CHECKER, func)


class UpdateCheckDoneEvent(wx.PyEvent):
    '''Simple event to check for updates.'''

    def __init__(self, data):
        '''Init Update Check Done Event.'''
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_UPDATE_CHECKER)
        self.data = data


class UpdateChecker(threading.Thread):
    def __init__(self, parent, current_version):
        threading.Thread.__init__(self)
        self._parent = parent
        self._current_version = current_version

    def run(self):
        try:
            response = requests.get(GITHUB_RELEASES_API, timeout=30)
            if response.status_code == 200:
                json_response = response.json()
                latest_version = json_response["tag_name"]
                print(latest_version)
                if version.parse(latest_version[1:]) > version.parse(self._current_version[1:]):
                    download_url = ''
                    download_name = ''
                    for asset in json_response['assets']:
                        if OS_MAP[sys.platform] in asset['name'].lower():
                            download_url = asset['browser_download_url']
                            download_name = asset['name']
                            break

                    wx.PostEvent(self._parent, UpdateCheckDoneEvent({
                        'update_available': True,
                        'latest_version': latest_version,
                        'download_url': download_url,
                        'download_name': download_name
                    }))
                else:
                    wx.PostEvent(self._parent, UpdateCheckDoneEvent({
                        'update_available': False
                    }))
        except Exception as ex:
            pass
