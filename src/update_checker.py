import wx
import sys

import threading
import json
import urllib

GITHUB_RELEASES_API = "https://api.github.com/repos/getodk/xlsform-offline/releases/latest"
GITHUB_MARKDOWN_API = "https://api.github.com/markdown/raw"

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
            response = urllib.request.urlopen(GITHUB_RELEASES_API)
            if response.getcode() == 200:
                json_response = json.load(response)
                latest_version = json_response["tag_name"]
                if latest_version[1:] > self._current_version:
                    download_url = ''
                    download_name = ''
                    for asset in json_response['assets']:
                        if OS_MAP[sys.platform] in asset['name'].lower():
                            download_url = asset['browser_download_url']
                            download_name = asset['name']
                            break

                    # second request is for markdown conversion 
                    data = json_response["body"].encode('utf-8')
                    headers = {'Content-Type': 'text/plain'}

                    request = urllib.request.Request(url=GITHUB_MARKDOWN_API, data=data, headers=headers)
                    html_body = urllib.request.urlopen(request).read().decode('utf-8')

                    wx.PostEvent(self._parent, UpdateCheckDoneEvent({
                        'update_available': True,
                        'latest_version': latest_version,
                        'download_url': download_url,
                        'download_name': download_name,
                        'update_desc': html_body
                    }))
                else:
                    wx.PostEvent(self._parent, UpdateCheckDoneEvent({
                        'update_available': False
                    }))
        except Exception as ex:
            print("EXCEPTION")
            print(ex)
            pass