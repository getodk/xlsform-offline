#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import webbrowser
import ntpath
import subprocess

import wx
import worker

# TODO pull out all strings
# TODO why is the first button selected

TITLE = 'ODK XLSForm Offline'

APP_QUIT = 1
APP_ABOUT = 2

MAIN_WINDOW_WIDTH = 475
MAIN_WINDOW_HEIGHT = 620
ABOUT_WINDOW_WIDTH = 360
ABOUT_WINDOW_HEIGHT = 365
MAX_PATH_LENGTH = 45
HEADER_SPACER = 6
CHOOSE_BORDER = 5
CHOOSE_SPACER = 0
OPTIONS_SPACER = 6

if sys.platform == 'darwin':
    MAIN_WINDOW_WIDTH = 500
    MAIN_WINDOW_HEIGHT = 750
    ABOUT_WINDOW_WIDTH = 360
    ABOUT_WINDOW_HEIGHT = 315
    MAX_PATH_LENGTH = 40
    HEADER_SPACER = 0
    CHOOSE_BORDER = 1
    CHOOSE_SPACER = 4
    OPTIONS_SPACER = 4

WORKER_FINISH = 'WORKER_FINISH'
WORKER_PROGRESS = 'WORKER_PROGRESS'
WORKER_PROGRESS_SLEEP = .05


class AboutFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title='About ' + TITLE,
                          size=(ABOUT_WINDOW_WIDTH, ABOUT_WINDOW_HEIGHT),
                          style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        html = HtmlWindow(self)
        html.SetStandardFonts()
        about = os.path.join('res','about.html')
        if getattr(sys, 'frozen', False):
            html.LoadPage(os.path.join(sys._MEIPASS, about))
        else:
            html.LoadPage(os.path.join('src', about))


class HtmlWindow(wx.html.HtmlWindow):
    def OnLinkClicked(self, link):
        webbrowser.open(link.GetHref())


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title,
                                        size=(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT),
                                        style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        self.input_file_path = u''
        self.output_folder_path = u''
        self.status_log = u''

        self.validate = False
        self.overwrite = False

        self.worker = None
        self.result_thread = None
        self.progress_thread = None

        self.about_window = None

        self.menu_bar = wx.MenuBar()
        self.file_menu = wx.Menu()
        self.help_menu = wx.Menu()

        self.quit_menu_item = wx.MenuItem(self.file_menu, APP_QUIT, '&Quit\tCtrl+Q')
        self.about_menu_item = wx.MenuItem(self.help_menu, APP_ABOUT, '&About ' + TITLE)

        self.file_menu.Append(self.quit_menu_item)
        self.help_menu.Append(self.about_menu_item)

        self.menu_bar.Append(self.file_menu, '&File')
        self.menu_bar.Append(self.help_menu, '&About')

        self.Bind(wx.EVT_MENU, self.on_quit, id=APP_QUIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=APP_ABOUT)

        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.SetMenuBar(self.menu_bar)

        self.parent_panel = wx.ScrolledWindow(self)
        self.parent_panel.SetScrollbars(1, 1, 1, 1)
        self.parent_box_sizer = wx.BoxSizer(wx.VERTICAL)

        self.about_button = wx.Button(self.parent_panel, label='About')
        self.about_button.Bind(wx.EVT_BUTTON, self.on_about)

        self.quit_button = wx.Button(self.parent_panel, label='Quit')
        self.quit_button.Bind(wx.EVT_BUTTON, self.on_quit)

        # header
        self.header_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.header_box_sizer.AddStretchSpacer()
        self.header_box_sizer.Add(self.about_button, proportion=0, flag=wx.LEFT | wx.RIGHT, border=5)
        self.header_box_sizer.Add(self.quit_button, proportion=0, flag=wx.LEFT | wx.RIGHT, border=5)

        # choose input file
        self.choose_input_static_box = wx.StaticBox(self.parent_panel,
                                                    label='1. Choose XLSForm (.xls or .xlsx) for conversion')
        self.choose_input_static_box_sizer = wx.StaticBoxSizer(self.choose_input_static_box, wx.HORIZONTAL)

        self.choose_file_button = wx.Button(self.parent_panel, label='Choose file...')
        self.choose_file_button.Bind(wx.EVT_BUTTON, self.on_open_file)
        self.chosen_file_text = wx.StaticText(self.parent_panel, label='', size=(-1, -1))

        self.choose_file_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.choose_file_box_sizer.Add(self.choose_file_button, proportion=0, flag=wx.LEFT | wx.RIGHT, border=0)
        self.choose_file_box_sizer.AddSpacer(CHOOSE_SPACER)
        self.choose_file_box_sizer.Add(self.chosen_file_text, proportion=1,
                                       flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                       border=CHOOSE_BORDER)
        self.choose_file_box_sizer.AddSpacer(CHOOSE_SPACER)
        self.choose_input_static_box_sizer.Add(self.choose_file_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL,
                                               border=5)

        # choose output folder
        self.choose_folder_label = '2. Choose location for output file(s)'
        self.choose_output_static_box = wx.StaticBox(self.parent_panel, label=self.choose_folder_label)
        self.choose_output_static_box_sizer = wx.StaticBoxSizer(self.choose_output_static_box, wx.HORIZONTAL)

        self.choose_folder_button = wx.Button(self.parent_panel, label='Choose location...')
        self.choose_folder_button.Bind(wx.EVT_BUTTON, self.on_open_folder)
        self.chosen_folder_text = wx.StaticText(self.parent_panel, label='', size=(-1, -1))

        self.choose_folder_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.choose_folder_box_sizer.Add(self.choose_folder_button, proportion=0, flag=wx.LEFT | wx.RIGHT, border=0)
        self.choose_folder_box_sizer.AddSpacer(CHOOSE_SPACER)
        self.choose_folder_box_sizer.Add(self.chosen_folder_text, proportion=1,
                                         flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                         border=CHOOSE_BORDER)
        self.choose_folder_box_sizer.AddSpacer(CHOOSE_SPACER)
        self.choose_output_static_box_sizer.Add(self.choose_folder_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL,
                                                border=5)

        # set conversion options
        self.set_options_static_box = wx.StaticBox(self.parent_panel, label='3. Set conversion options')
        self.set_options_static_box_sizer = wx.StaticBoxSizer(self.set_options_static_box, wx.VERTICAL)

        self.overwrite_label = 'Overwrite existing output file(s)'
        self.overwrite_checkbox = wx.CheckBox(self.parent_panel, label=self.overwrite_label, size=(-1, -1))
        self.overwrite_checkbox.SetValue(self.overwrite)
        self.Bind(wx.EVT_CHECKBOX, self.toggle_overwrite, id=self.overwrite_checkbox.GetId())

        self.validate_label = 'Validate converted XForm with ODK Validate'
        if self.is_java_installed():
            self.validate = True
            self.validate_checkbox = wx.CheckBox(self.parent_panel, label=self.validate_label, size=(-1, -1))
            self.Bind(wx.EVT_CHECKBOX, self.toggle_validate, id=self.validate_checkbox.GetId())
        else:
            self.validate = False
            self.validate_checkbox = wx.CheckBox(self.parent_panel, label=self.validate_label + ' (Requires Java)')
            self.validate_checkbox.Disable()
            self.Bind(wx.EVT_CHECKBOX, self.toggle_validate, id=self.validate_checkbox.GetId())
        self.validate_checkbox.SetValue(self.validate)

        self.set_options_static_box_sizer.Add(self.overwrite_checkbox, flag=wx.LEFT | wx.TOP, border=5)
        self.set_options_static_box_sizer.AddStretchSpacer()
        self.set_options_static_box_sizer.Add(self.validate_checkbox, flag=wx.LEFT | wx.TOP, border=5)
        self.set_options_static_box_sizer.AddStretchSpacer()
        self.set_options_static_box_sizer.AddSpacer(OPTIONS_SPACER)

        # start conversion
        self.start_conversion_static_box = wx.StaticBox(self.parent_panel, label='4. Run conversion')
        self.start_conversion_box_sizer = wx.StaticBoxSizer(self.start_conversion_static_box, wx.VERTICAL)

        self.status_text_ctrl = wx.TextCtrl(self.parent_panel, size=(-1, 200), style=wx.TE_MULTILINE | wx.TE_LEFT)
        self.status_text_ctrl.SetEditable(False)
        self.status_text_ctrl.SetValue(self.status_log)
        self.status_gauge = wx.Gauge(self.parent_panel, range=1, size=(-1, -1))

        self.action_button = wx.Button(self.parent_panel, label='Run')
        self.action_button.Bind(wx.EVT_BUTTON, self.on_action)
        self.action_button.Disable()

        self.status_gauge_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status_gauge_box_sizer.Add(self.status_gauge, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)
        self.status_gauge_box_sizer.AddSpacer(CHOOSE_SPACER)
        self.status_gauge_box_sizer.Add(self.action_button, proportion=0, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                                        border=2.5)
        self.status_gauge_box_sizer.AddSpacer(CHOOSE_SPACER)
        self.start_conversion_box_sizer.Add(self.status_gauge_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL,
                                            border=5)

        self.start_conversion_box_sizer.Add(self.status_text_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # build ui
        self.parent_box_sizer.AddSpacer(15)
        self.parent_box_sizer.Add(self.header_box_sizer, proportion=0, flag=wx.EXPAND | wx.RIGHT | wx.LEFT, border=20)
        self.parent_box_sizer.AddSpacer(HEADER_SPACER)
        self.parent_box_sizer.Add(self.choose_input_static_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.parent_box_sizer.Add(self.choose_output_static_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.parent_box_sizer.Add(self.set_options_static_box_sizer, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.parent_box_sizer.Add(self.start_conversion_box_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.parent_panel.SetSizer(self.parent_box_sizer)

        worker.evt_result(self, self.on_result)
        worker.evt_progress(self, self.on_progress)

        self.Centre()
        self.Show()

    @staticmethod
    def shorten_string(string, max_length):
        if len(string) >= max_length:
            return '...' + string[len(string) - max_length:len(string)]
        else:
            return string

    def on_open_file(self, e):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message='Choose a file',
            defaultFile='',
            wildcard='XLSForm files (*.xls,*.xlsx)|*.xls;*.xlsx',
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.input_file_path = dlg.GetPath()
            self.chosen_file_text.SetLabel(self.shorten_string(self.input_file_path, MAX_PATH_LENGTH))
            self.output_folder_path = ntpath.dirname(self.input_file_path)
            self.chosen_folder_text.SetLabel(self.shorten_string(self.output_folder_path, MAX_PATH_LENGTH))
            if self.input_file_path and self.output_folder_path:
                self.action_button.Enable()
            else:
                self.action_button.Disable()
        dlg.Destroy()

    def on_open_folder(self, e):
        """
        Create and show the Open DirDialog
        """
        dlg = wx.DirDialog(
            self, message='Choose a location',
            defaultPath=self.output_folder_path,
            style=wx.DD_DEFAULT_STYLE | wx.DD_CHANGE_DIR)
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.output_folder_path = dlg.GetPath()
            self.chosen_folder_text.SetLabel(self.shorten_string(self.output_folder_path, MAX_PATH_LENGTH))
            if self.input_file_path and self.output_folder_path:
                self.action_button.Enable()
            else:
                self.action_button.Disable()
        dlg.Destroy()

    def on_action(self, e):
        if self.action_button.GetLabel() == 'Run':
            self.action_button.Disable()
            # thread that does the work
            self.result_thread = worker.Result(self, self.input_file_path, self.output_folder_path, self.validate,
                                               self.overwrite)
            # thread that updates the progress bar
            self.progress_thread = worker.Progress(self, WORKER_PROGRESS_SLEEP)

            self.enable_ui(False)

    def toggle_validate(self, event):
        self.validate = not self.validate

    def toggle_overwrite(self, event):
        self.overwrite = not self.overwrite

    def on_quit(self, e):
        self.Destroy()
        if self.about_window:
            self.about_window.Close()

    def on_about(self, e):
        if self.about_window:
            self.about_window.Close()
        self.about_window = AboutFrame(None)
        self.about_window.Centre()
        self.about_window.Show()

    def on_result(self, event):
        if event.data is WORKER_FINISH:
            self.progress_thread.abort()
            self.status_text_ctrl.AppendText('-----------------------------------------------------\n\n')
            self.action_button.Enable()
            self.enable_ui(True)
            self.action_button.SetLabel('Run')
            self.status_gauge.SetValue(1)
            self.status_gauge.SetValue(0)
        else:
            self.status_text_ctrl.AppendText(event.data)

    def on_progress(self, event):
        if self.result_thread is not None and self.result_thread.is_alive():
            self.status_gauge.Pulse()

    @staticmethod
    def is_java_installed():

        startupinfo = None
        # needed to hide the pop up cmd window
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        java_version = None
        java_regex = re.compile(b'(java|openjdk) version')
        try:
            java_version = subprocess.Popen(['java', '-version'], stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, shell=False, startupinfo=startupinfo).communicate()[
                1].splitlines()[0]
        except:
            pass

        return java_version and java_regex.match(java_version)


    def enable_ui(self, enable):
        # Turns UI elements on and off
        self.choose_file_button.Enable(enable)
        self.choose_folder_button.Enable(enable)
        self.overwrite_checkbox.Enable(enable)
        if self.is_java_installed():
            self.validate_checkbox.Enable(enable)


if __name__ == '__main__':
    app = wx.App()
    app.SetAppName(TITLE)
    MainFrame(None, title=TITLE)
    app.MainLoop()