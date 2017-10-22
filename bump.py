import os
import urllib

import sublime

from . import defaults
from . import settings as conf
from . import parser
from . import cache
from . import request
from . import log

class Bump:
    def get_focused_view_id(self, view):
        active_view = view.window().active_view()

        for view in view.window().views():
            if view == active_view:
                return view

    def file_supported(self, view):
        full_filename = view.file_name()
        if not full_filename:
            return False
        filename = os.path.split(full_filename)[1]
        # sublime.status_message(file_extension)
        return filename in conf.settings.get('supported_filenames', defaults.get_supported_filenames())

    def from_cache_or_fetch(self, package, distribution_mode, vid, callback):
        cached = cache.get_by_package(package, distribution_mode, vid)
        if cached:
            callback(cached)
            return

        try: request.fetch_package_version(package, distribution_mode, callback)
        except urllib.error.URLError as e:
            if e.code == 404 and distribution_mode != 'latest':
                request.fetch_package_version(package, 'latest', callback)

    def run_bump_with_mode(self, view, edit, distribution_mode):
        if not self.file_supported(view): return
        region = parser.get_active_region(view)
        line_text = parser.get_text_from_line(view, region)
        if not line_text: return

        package, version = parser.get_current_package(line_text)
        vid = view.id()

        def callback(version):
            transfrom.format_version_on_line(view, edit, region, version)

        self.from_cache_or_fetch(package, distribution_mode, vid, callback)

    def log_version_for_view(self, view):
        if not self.file_supported(view):
            return

        view = self.get_focused_view_id(view)

        if view is None:
            return

        vid = view.id()

        # Get active region
        region = parser.get_active_region(view)

        if region == None:
           return

        # Get parent package key for active region.
        parent_key = parser.get_parent_key(view, region)
        target_fields = conf.settings.get('dependency_fields', defaults.get_dependency_fields())

        # Prevent parsing values from other fields.
        if not parent_key or parent_key not in target_fields:
            return

        line_text = parser.get_text_from_line(view, region)

        if not line_text:
            return

        package, version = parser.get_current_package(line_text)
        distribution_mode = conf.settings.get('distribution_mode', defaults.get_distribution_mode())

        def callback(version):
            cache.set_package(package, distribution_mode, vid, version)
            with_tooltip = conf.settings.get('tooltip', defaults.get_tooltip())
            log.log_version(view, package, version, with_tooltip)

        self.from_cache_or_fetch(package, distribution_mode, vid, callback)


    def log_version_for_active_view(self):
        view = sublime.active_window().active_view()
        self.log_version_for_view(view)

    def is_scratch(self, view):
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


if 'plugin_is_loaded' not in globals():
    worker = Bump()
