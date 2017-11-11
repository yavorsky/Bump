import json
import os
from string import Template

import sublime
import sublime_plugin

from . import parser
from . import log
from . import request
from . import cache
from . import transfrom
from . import commands
from . import settings as conf
from . import persist

def plugin_loaded():
    """Entry point for SL plugins."""
    conf.plugin_is_loaded = True
    conf.settings.load()
    log.printf('debug mode:', 'on' if conf.debug_mode() else 'off')

    plugin = Bump.shared_plugin()
    conf.settings.on_update_call(Bump.on_settings_updated)

class Bump(sublime_plugin.EventListener):
    def __init__(self, *args, **kwargs):
        """Initialize a new instance."""
        super().__init__(*args, **kwargs)

        self.__class__.shared_instance = self

    @classmethod
    def shared_plugin(cls):
        """Return the plugin instance."""
        return cls.shared_instance

    @classmethod
    def on_settings_updated(cls, setting):
        persist.worker.log_version_for_active_view()

    def on_selection_modified_async(self, view):
        self.display_version_for_line(view, tooltip=True)

    def display_version_for_line(self, view, tooltip=False):
        if persist.worker.is_scratch(view):
           return
        persist.worker.log_version_for_view(view)
