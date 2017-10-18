import json
import os
from string import Template

import sublime
import sublime_plugin

from . import parser, manager
from . import log
from . import request
from . import cache
from . import transfrom

def get_focused_view_id(view):
    active_view = view.window().active_view()

    for view in view.window().views():
        if view == active_view:
            return view

def file_supported(view):
    full_filename = view.file_name()
    if not full_filename:
        return False
    filename = os.path.split(full_filename)[1]
    # sublime.status_message(file_extension)
    return filename in manager.get_supported_filenames()

def from_cache_or_fetch(package, version_mode, vid, callback):
    cached = cache.get_by_package(package, version_mode, vid)
    if cached:
        callback(cached)
        return

    request.fetch_package_version(package, version_mode, callback)

def run_bump_with_mode(view, edit, version_mode):
    if not file_supported(view): return
    region = parser.get_active_region(view)
    line_text = parser.get_text_from_line(view, region)
    if not line_text: return

    package, version = parser.get_current_package(line_text)
    vid = view.id()

    def callback(version):
        transfrom.format_version_on_line(view, edit, region, version)

    from_cache_or_fetch(package, version_mode, vid, callback)

class BumpLatestVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_bump_with_mode(self.view, edit, 'latest')

class BumpNextVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_bump_with_mode(self.view, edit, 'next')

class SwitchLatestVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_bump_with_mode(self.view, edit, 'next')

class SwitchNextVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        run_bump_with_mode(self.view, edit, 'next')

# class BumpAllVersionsCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         self.view.insert(edit, 0, "111")

# class PrintVersionCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         # sublime.set_timeout(lambda: sublime.status_message('Selection(s) already formatted.'), 0)
#         window = sublime.active_window()
#         if window:
#             self.on_focus(window.active_view())
#     def on_focus(self, view):
#         print(view.size())

class SublimeBump(sublime_plugin.EventListener):
    def on_selection_modified_async(self, view):
        #id = get_focused_view_id(view)
        # sublime.status_message(str(view.name))
        self.display_version_for_line(view, tooltip=True)
        #sublime.status_message(str(view.sel()))
        # allcontent = sublime.Region(0, view.size())
        # view.replace(view, allcontent, 'Hello, World!')

    def display_version_for_line(self, view, tooltip=False):
        if self.is_scratch(view):
           return

        if not file_supported(view):
            return

        view = get_focused_view_id(view)

        if view is None:
            return

        vid = view.id()

        region = parser.get_active_region(view)

        if region == None:
           return

        text_from_point = view.substr(sublime.Region(0, region.begin()))

        parent_key = parser.get_parent_key(text_from_point)
        if not parent_key or parent_key not in manager.get_dependency_fields():
            return

        line_text = parser.get_text_from_line(view, region)
        # try:
        #     lineno = view.rowcol(region.begin())[0]
        #     lineText = view.substr(view.line(region)).strip()
        # #     # selectedText = view.substr(region.begin())
        # except IndexError:
        #     lineno = -1
        #     lineText = None

        if not line_text:
            return

        package, version = parser.get_current_package(line_text)
        version_mode = manager.get_package_version()

        #package_str = package + version

        # if cache.in_cache(package, version_mode, vid):
        #     log.log_version(view, package, cache.get_by_package(package, version_mode, vid))
        #     return

        def callback(version):
            cache.set_package(package, version_mode, vid, version)
            log.log_version(view, package, version)

        # request.fetch_package_version(package, version_mode, callback)
        from_cache_or_fetch(package, version_mode, vid, callback)

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

    def is_scratch(self, view):
        """
        Return whether a view is effectively scratch.

        There is a bug (or feature) in the current ST3 where the Find panel
        is not marked scratch but has no window.

        There is also a bug where settings files opened from within .sublime-package
        files are not marked scratch during the initial on_modified event, so we have
        to check that a view with a filename actually exists on disk if the file
        being opened is in the Sublime Text packages directory.

        """

        if view.is_scratch() or view.is_read_only() or view.window() is None or view.settings().get("repl") is not None:
            return True
        elif (
            view.file_name() and
            view.file_name().startswith(sublime.packages_path() + os.path.sep) and
            not os.path.exists(view.file_name())
        ):
            return True
        else:
            return False

