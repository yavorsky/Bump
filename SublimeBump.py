import json
from urllib import parse, request
import os
import re
from string import Template

import sublime
import sublime_plugin

versions = {
    
}

views = {
    
}

supported_filenames = [
    'package.json'
]

dependency_fields = [
    'dependencies',
    'devDependencies',
    'peerDependencies'
]

default_registry = 'https://registry.npmjs.org';
default_version = 'latest' # could be next

# class ExampleCommand(sublime_plugin.TextCommand):
#   def run(self, edit):
#     data = request.urlopen('http://echo.jsontest.com/key/value/one/twos')
#     res_body = data.read()
#     res_obj = json.loads(res_body.decode("utf-8"))
#     self.view.insert(edit, 0, json.dumps(res_obj))

class BumpLineVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.insert(edit, 0, "111")

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
        id = self.get_focused_view_id(view)
        # sublime.status_message(str(view.name))
        self.display_version_for_line(view, tooltip=True)
        #sublime.status_message(str(view.sel()))
        # allcontent = sublime.Region(0, view.size())
        # view.replace(view, allcontent, 'Hello, World!')

    def get_registry(self):
        return default_registry

    def get_package_version(self):
        return default_version

    def display_version_for_line(self, view, tooltip=False):
        if self.is_scratch(view):
           return

        #if not self.format_supported(view):
            #return

        view = self.get_focused_view_id(view)

        if view is None:
            return

        vid = view.id()

        try:
            selection = view.sel();
            region = selection[0]
        except IndexError:
            region = None


        if region == None:
            return

        text_from_point = view.substr(sublime.Region(0, region.begin()))

        parent_key = self.get_parent_key(text_from_point)
        if not parent_key or parent_key not in dependency_fields:
            return

        try:
            lineno = view.rowcol(region.begin())[0]
            lineText = view.substr(view.line(region)).strip()
        #     # selectedText = view.substr(region.begin())
        except IndexError:
            lineno = -1
            lineText = None

        if not lineText:
            return

        package, version = self.get_current_version(lineText)

        if vid in versions and package in versions[vid]:
            self.log_version(view, package, versions[vid][package])

        def callback(version):
            if (vid not in versions):
                versions[vid] = {}
    
            versions[vid][package] = version

        self.fetch_latest_version(package, callback)

        #self.update_log(view, version);
        # text = self.get_text(view)
        # sublime.status_message(lineText)
        #self.update_log(view, parent_key);
        #self.update_log(view, view.substr(self.get_lines(view)[lineno]))
        # self.update_log(view, str(len(upper_text)));

    # def get_lines(self, view):
        # return view.split_by_newlines(sublime.Region(0, view.size()))

    def get_request(self, pathname):
        webURL = request.urlopen(pathname)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        return json.loads(data.decode(encoding))

    def fetch_latest_version(self, package, callback = None):
        registry = self.get_registry()
        version = self.get_package_version()
        pathname = os.path.join(registry, package)
        pathname = Template('$pathname?version=$version').substitute(pathname=pathname, version=version)
        response = self.get_request(pathname)
        if (callback):
            callback(response['version'])

    def log_version(self, view, package, version):
        formatted = Template('$package: $version').substitute(package=package, version=version)
        self.update_log(view, formatted);

    def get_current_version(self, text):
        lineRe = r'"\s?(.+)\s?"\s?:?\s?"(.+)'
        groups = re.search(lineRe, text)
        return [groups.group(1), groups.group(2)]

    def get_parent_key(self, text):
        upper_field_re = r'"\s?(.+)\s?"\s?:\s?{'
        parent_keys = re.findall(upper_field_re, text)
        if not len(parent_keys):
            return None
        return parent_keys[-1];

    def update_log(self, view, text):
        self.unset_log(view)
        self.set_log(view, text)

    def set_log(self, view, lineText):
        view.set_status('sublimebump', lineText)

    def unset_log(self, view):
        view.erase_status('sublimebump')

    def get_text(self, view):
        return view.substr(sublime.Region(0, view.size()))

    def format_supported(self, view):
        full_filename = view.file_name()
        filename = os.path.split(full_filename)[1]
        # sublime.status_message(file_extension)
        return filename in supported_filenames

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


    def get_focused_view_id(self, view):
        """
        Return the focused view which shares view's buffer.

        When updating the status, we want to make sure we get
        the selection of the focused view, since multiple views
        into the same buffer may be open.

        """
        active_view = view.window().active_view()

        for view in view.window().views():
            if view == active_view:
                return view
