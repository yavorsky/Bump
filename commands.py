# coding: utf-8
#
#
# Written by Artem Yavorsky
#
# Project: https://github.com/yavorsky/SublimeBump
# License: MIT
#


import sublime_plugin

from . import defaults
from . import persist
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
        return self.settings[index]


def choose_setting_command(setting, preview):
    def decorator(cls):
        def init(self, window):
            super(cls, self).__init__(window, setting, preview)

        def run(self, **kwargs):
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
        persist.worker.log_version_for_active_view()

class BumpLatestVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        persist.worker.run_bump_with_mode(self.view, edit, 'latest')

class BumpNextVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        persist.worker.run_bump_with_mode(self.view, edit, 'next')

class SublimebumpEditCommand(sublime_plugin.TextCommand):
    """A plugin command used to generate an edit object for a view."""

    def run(self, edit):
        """Run the command."""
        conf.edit(self.view.id(), edit)
