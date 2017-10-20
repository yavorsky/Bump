# coding: utf-8
#
# commands.py
# Part of SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Ryan Hileman and Aparajita Fishman
#
# Project: https://github.com/SublimeLinter/SublimeLinter3
# License: MIT
#

"""This module implements the Sublime Text commands provided by SublimeLinter."""

import datetime
from fnmatch import fnmatch
from glob import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
from textwrap import TextWrapper
from threading import Thread
import time

import sublime
import sublime_plugin

from . import defaults
from . import bump
from . import settings as conf

class ChooseSettingCommand(sublime_plugin.WindowCommand):
    """An abstract base class for commands that choose a setting from a list."""

    def __init__(self, window, setting=None, preview=False):
        """Initialize a new instance."""
        super().__init__(window)
        self.setting = setting
        self._settings = None
        self.preview = preview

    def description(self, **args):
        """Return the visible description of the command, used in menus."""
        return args.get('value', None)

    def is_checked(self, **args):
        """Return whether this command should be checked in a menu."""
        if 'value' not in args:
            return False

        item = self.transform_setting(args['value'], matching=True)
        setting = self.setting_value(matching=True)
        return item == setting

    def _get_settings(self):
        """Return the list of settings."""
        if self._settings is None:
            self._settings = self.get_settings()

        return self._settings

    settings = property(_get_settings)

    def get_settings(self):
        """Return the list of settings. Subclasses must override this."""
        raise NotImplementedError

    def transform_setting(self, setting, matching=False):
        """
        Transform the display text for setting to the form it is stored in.

        By default, returns a lowercased copy of setting.

        """
        return setting.lower()

    def setting_value(self, matching=False):
        """Return the current value of the setting."""
        return self.transform_setting(conf.settings.get(self.setting, ''), matching=matching)

    def on_highlight(self, index):
        """If preview is on, set the selected setting."""
        if self.preview:
            self.set(index)

    def choose(self, **kwargs):
        """
        Choose or set the setting.

        If 'value' is in kwargs, the setting is set to the corresponding value.
        Otherwise the list of available settings is built via get_settings
        and is displayed in a quick panel. The current value of the setting
        is initially selected in the quick panel.

        """

        if 'value' in kwargs:
            setting = self.transform_setting(kwargs['value'])
        else:
            setting = self.setting_value(matching=True)

        index = 0

        for i, s in enumerate(self.settings):
            if isinstance(s, (tuple, list)):
                s = self.transform_setting(s[0])
            else:
                s = self.transform_setting(s)

            if s == setting:
                index = i
                break

        if 'value' in kwargs:
            self.set(index)
        else:
            self.previous_setting = self.setting_value()

            self.window.show_quick_panel(
                self.settings,
                on_select=self.set,
                selected_index=index,
                on_highlight=self.on_highlight)

    def set(self, index):
        """Set the value of the setting."""
        if index == -1:
            if self.settings_differ(self.previous_setting, self.setting_value()):
                self.update_setting(self.previous_setting)

            return

        setting = self.selected_setting(index)

        if isinstance(setting, (tuple, list)):
            setting = setting[0]

        setting = self.transform_setting(setting)
        if not self.settings_differ(conf.settings.get(self.setting, ''), setting):
            return

        self.update_setting(setting)

    def update_setting(self, value):
        """Update the setting with the given value."""
        conf.settings.set(self.setting, value, changed=True)
        self.setting_was_changed(value)
        conf.settings.save()

    def settings_differ(self, old_setting, new_setting):
        """Return whether two setting values differ."""
        if isinstance(new_setting, (tuple, list)):
            new_setting = new_setting[0]

        new_setting = self.transform_setting(new_setting)
        return new_setting != old_setting

    def selected_setting(self, index):
        """
        Return the selected setting by index.

        Subclasses may override this if they want to return something other
        than the indexed value from self.settings.

        """
        return self.settings[index]

    def setting_was_changed(self, setting):
        """
        Do something after the setting value is changed but before settings are saved.

        Subclasses may override this if further action is necessary after
        the setting's value is changed.

        """
        pass


def choose_setting_command(setting, preview):
    """Return a decorator that provides common methods for concrete subclasses of ChooseSettingCommand."""

    def decorator(cls):
        def init(self, window):
            super(cls, self).__init__(window, setting, preview)

        def run(self, **kwargs):
            """Run the command."""
            self.choose(**kwargs)

        cls.setting = setting
        cls.__init__ = init
        cls.run = run
        return cls

    return decorator

@choose_setting_command('distribution_mode', preview=False)
class ChooseDistributionMode(ChooseSettingCommand):
    def get_settings(self):
        return [[name.capitalize(), description] for name, description in defaults.VERSION_MODES]

    def setting_was_changed(self, setting):
        bump.worker.log_version_for_active_view()

class BumpLatestVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        bump.worker.run_bump_with_mode(self.view, edit, 'latest')

class BumpNextVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        bump.worker.run_bump_with_mode(self.view, edit, 'next')
