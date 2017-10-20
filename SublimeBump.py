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
from . import bump

def plugin_loaded():
    """Entry point for SL plugins."""
    conf.plugin_is_loaded = True
    conf.settings.load()
    log.printf('debug mode:', 'on' if conf.debug_mode() else 'off')

    plugin = SublimeBump.shared_plugin()
    conf.settings.on_update_call(SublimeBump.on_settings_updated)

    # # This ensures we lint the active view on a fresh install
    # window = sublime.active_window()

    # if window:
    #     plugin.on_selection_modified_async(window.active_view())

class SublimeBump(sublime_plugin.EventListener):
    def __init__(self, *args, **kwargs):
        """Initialize a new instance."""
        super().__init__(*args, **kwargs)

        # Keeps track of which views we have assigned linters to
        self.loaded_views = set()

        # Keeps track of which views have actually been linted
        self.linted_views = set()

        self.__class__.shared_instance = self

    @classmethod
    def shared_plugin(cls):
        """Return the plugin instance."""
        return cls.shared_instance

    @classmethod
    def on_settings_updated(cls):
        bump.worker.log_version_for_active_view()

    def on_selection_modified_async(self, view):
        #id = get_focused_view_id(view)
        # sublime.status_message(str(view.name))
        self.display_version_for_line(view, tooltip=True)
        #sublime.status_message(str(view.sel()))
        # allcontent = sublime.Region(0, view.size())
        # view.replace(view, allcontent, 'Hello, World!')

    def display_version_for_line(self, view, tooltip=False):
        if bump.worker.is_scratch(view):
           return
        bump.worker.log_version_for_view(view)

        # if not file_supported(view):
        #     return

        # view = get_focused_view_id(view)

        # if view is None:
        #     return

        # vid = view.id()

        # region = parser.get_active_region(view)

        # if region == None:
        #    return

        # text_from_point = view.substr(sublime.Region(0, region.begin()))

        # parent_key = parser.get_parent_key(text_from_point)
        # if not parent_key or parent_key not in manager.get_dependency_fields():
        #     return

        # line_text = parser.get_text_from_line(view, region)
        # # try:
        # #     lineno = view.rowcol(region.begin())[0]
        # #     lineText = view.substr(view.line(region)).strip()
        # # #     # selectedText = view.substr(region.begin())
        # # except IndexError:
        # #     lineno = -1
        # #     lineText = None

        # if not line_text:
        #     return

        # package, version = parser.get_current_package(line_text)
        # distribution_mode = manager.get_package_version()

        # #package_str = package + version

        # # if cache.in_cache(package, distribution_mode, vid):
        # #     log.log_version(view, package, cache.get_by_package(package, distribution_mode, vid))
        # #     return

        # def callback(version):
        #     cache.set_package(package, distribution_mode, vid, version)
        #     log.log_version(view, package, version)

        # # request.fetch_package_version(package, distribution_mode, callback)
        # from_cache_or_fetch(package, distribution_mode, vid, callback)

        #self.update_log(view, version);
        # text = self.get_text(view)
        # sublime.status_message(line_text)
        #self.update_log(view, parent_key);
        #self.update_log(view, view.substr(self.get_lines(view)[lineno]))
        # self.update_log(view, str(len(upper_text)));

    # def get_lines(self, view):
        # return view.split_by_newlines(sublime.Region(0, view.size()))

    # def get_request(self, pathname):
    #     webURL = request.urlopen(pathname)
    #     data = webURL.read()
    #     encoding = webURL.info().get_content_charset('utf-8')
    #     return json.loads(data.decode(encoding))

    # def fetch_package_version(self, package, version, callback = None):
    #     registry = nodeManager.get_registry()
    #     pathname = os.path.join(registry, package)
    #     pathname = Template('$pathname?version=$version').substitute(pathname=pathname, version=version)
    #     response = self.get_request(pathname)
    #     if (callback):
    #         callback(response['version'])

class SublimebumpEditCommand(sublime_plugin.TextCommand):
    """A plugin command used to generate an edit object for a view."""

    def run(self, edit):
        """Run the command."""
        conf.edit(self.view.id(), edit)
