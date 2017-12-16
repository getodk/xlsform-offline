#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import ntpath
import time
import tempfile
import shutil
import threading

import wx.html

import main
import pyxform.xls2json as xls2json
import pyxform.builder as builder
from pyxform.utils import sheet_to_csv, has_external_choices


EVT_RESULT_ID = wx.NewId()
EVT_PROGRESS_ID = wx.NewId()


def evt_progress(win, func):
    '''Define Progress Event.'''
    win.Connect(-1, -1, EVT_PROGRESS_ID, func)


def evt_result(win, func):
    '''Define Result Event.'''
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ProgressEvent(wx.PyEvent):
    '''Simple event to update progress.'''

    def __init__(self, data):
        '''Init Progress Event.'''
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PROGRESS_ID)


class WorkEvent(wx.PyEvent):
    '''Simple event to carry arbitrary work data.'''

    def __init__(self, data):
        '''Init Result Event.'''
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# Thread class that executes processing
class Progress(threading.Thread):
    '''Progress Class.'''

    def __init__(self, notify_window, sleep_time):
        '''Init progress Class.'''
        threading.Thread.__init__(self)
        self._notify_window = notify_window
        self.aborted = False

        self.sleep_time = sleep_time
        self.start()

    def abort(self):
        self.aborted = True

    def run(self):
        while not self.aborted:
            wx.PostEvent(self._notify_window, ProgressEvent(main.WORKER_PROGRESS))
            time.sleep(self.sleep_time)
        return


# Thread class that executes processing
class Result(threading.Thread):
    '''Result Class.'''

    def __init__(self, notify_window, input_file_path, output_path, validate, overwrite):
        '''Init worker Class.'''
        threading.Thread.__init__(self)
        self._notify_window = notify_window
        self.data = None
        self.input_file_path = input_file_path

        self.file_name = ntpath.basename(self.input_file_path).split('.')[0]
        self.output_path = output_path + str(os.path.sep) + self.file_name

        self.validate = validate
        self.overwrite = overwrite

        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):

        single_file = True
        start_message = 'Input file: ' + self.input_file_path + '\n\n'
        wx.PostEvent(self._notify_window, WorkEvent(start_message))

        try:

            warnings = []

            json_survey = xls2json.parse_file_to_json(self.input_file_path, warnings=warnings)
            survey = builder.create_survey_element_from_dict(json_survey)

            # need a temp file because print_xform_to_file automatically creates the file
            temp_dir = tempfile.mkdtemp()
            survey.print_xform_to_file(temp_dir + str(os.path.sep) + self.file_name + '.xml', validate=self.validate,
                                       warnings=warnings)

            if has_external_choices(json_survey):
                single_file = False
                choices_exported = sheet_to_csv(self.input_file_path, temp_dir + str(os.path.sep) + 'itemsets.csv',
                                                'external_choices')
                if not choices_exported:
                    warnings.append('Could not export itemsets.csv, perhaps the external choices sheet is missing.')

            if warnings:
                wx.PostEvent(self._notify_window, WorkEvent('ODK XLSForm Offline Warnings:\n'))
                # need to add whitespace to beginning to prevent truncation of forms with many warnings.
                for warning in warnings:
                    # warning = warning.replace('XForm Parse Warning: Warning: ', '').replace('    ', '')
                    wx.PostEvent(self._notify_window, WorkEvent(' ' + warning.strip() + '\n'))
                wx.PostEvent(self._notify_window, WorkEvent('\n'))

            if single_file:
                output_path_test = self.output_path + '.xml'
                output_path_template = self.output_path + ' ({0}).xml'
            else:
                output_path_test = self.output_path
                output_path_template = self.output_path + ' ({0})'

            if not self.overwrite and os.path.exists(output_path_test):
                # find an unused name
                i = 1
                while os.path.exists(output_path_template.format(i)):
                    i += 1
                output_path_test = output_path_template.format(i)

            if single_file:
                shutil.copyfile(temp_dir + str(os.path.sep) + self.file_name + '.xml', output_path_test)
            else:
                if self.overwrite:
                    shutil.rmtree(self.output_path, True)
                shutil.copytree(temp_dir, output_path_test)

            finish_message = 'Output file(s): ' + output_path_test + '\n\n'
            wx.PostEvent(self._notify_window, WorkEvent(finish_message))

        except Exception as e:

            exception_text = str(e)
            exception_text = exception_text.replace('>> Something broke the parser. See above for a hint.', '')
            exception_text = exception_text.replace('Result: Invalid', '')
            exception_text = exception_text.replace('\n\n', '\n')

            validate_regex = re.compile('ODK Validate')
            if not (validate_regex.match(exception_text)):
                wx.PostEvent(self._notify_window, WorkEvent('ODK XLSForm Offline Errors:\n'))
                wx.PostEvent(self._notify_window, WorkEvent(exception_text.strip() + '\n'))
                wx.PostEvent(self._notify_window, WorkEvent('\n'))
            else:
                wx.PostEvent(self._notify_window, WorkEvent(exception_text.strip() + '\n\n'))

        # special message to main thread
        wx.PostEvent(self._notify_window, WorkEvent(main.WORKER_FINISH))
        return
