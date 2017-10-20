import sublime

from . import SublimeBump

def merge_user_settings(settings):
    """Return the default linter settings merged with the user's settings."""

    default = settings.get('default', {})
    user = settings.get('user', {})

    if user:
        linters = default.pop('linters', {})
        user_linters = user.get('linters', {})

        for name, data in user_linters.items():
            if name in linters:
                linters[name].update(data)
            else:
                linters[name] = data

        default['linters'] = linters

        user.pop('linters', None)
        default.update(user)

    return default

class Settings:
    def __init__(self):
        """Initialize a new instance."""
        self.settings = {}
        self.previous_settings = {}
        self.changeset = set()
        self.plugin_settings = None
        self.on_update_callback = None

    def load(self, force=False):
        if force or not self.settings:
            self.observe()
            self.on_update()
            self.observe_prefs()

    def has_setting(self, setting):
        """Return whether the given setting exists."""
        return setting in self.settings

    def get(self, setting, default=None):
        """Return a plugin setting, defaulting to default if not found."""
        return self.settings.get(setting, default)

    def set(self, setting, value, changed=False):
        """
        Set a plugin setting to the given value.

        Clients of this module should always call this method to set a value
        instead of doing settings['foo'] = 'bar'.

        If the caller knows for certain that the value has changed,
        they should pass changed=True.

        """
        self.copy()
        self.settings[setting] = value

        if changed:
            self.changeset.add(setting)

    def pop(self, setting, default=None):
        """
        Remove a given setting and return default if it is not in self.settings.

        Clients of this module should always call this method to pop a value
        instead of doing settings.pop('foo').

        """
        self.copy()
        return self.settings.pop(setting, default)

    def copy(self):
        """Save a copy of the plugin settings."""
        self.previous_settings = deepcopy(self.settings)

    def observe_prefs(self, observer=None):
        """Observe changes to the ST prefs."""
        prefs = sublime.load_settings('Preferences.sublime-settings')
        prefs.clear_on_change('sublimebump-pref-settings')
        prefs.add_on_change('sublimebump-pref-settings', observer or self.on_prefs_update)

    def observe(self, observer=None):
        """Observer changes to the plugin settings."""
        self.plugin_settings = sublime.load_settings('SublimeBump.sublime-settings')
        self.plugin_settings.clear_on_change('sublimebump-persist-settings')
        self.plugin_settings.add_on_change('sublimebump-persist-settings',
                                           observer or self.on_update)

    def on_update_call(self, callback):
        """Set a callback to call when user settings are updated."""
        self.on_update_callback = callback

    def on_update(self):
        """
        Update state when the user settings change.

        The settings before the change are compared with the new settings.
        Depending on what changes, views will either be redrawn or relinted.

        """

        settings = merge_user_settings(self.plugin_settings)
        self.settings.clear()
        self.settings.update(settings)

        if (
            '@disable' in self.changeset or
            self.previous_settings.get('@disable', False) != self.settings.get('@disable', False)
        ):
            need_refetch = True
            self.changeset.discard('@disable')
        else:
            need_refetch = False
        # if (
        #     'paths' in self.changeset or
        #     (self.previous_settings and
        #      self.previous_settings.get('paths') != self.settings.get('paths'))
        # ):
        #     need_relint = True
        #     util.clear_path_caches()
        #     self.changeset.discard('paths')

        # Add python paths if they changed
        # if (
        #     'python_paths' in self.changeset or
        #     (self.previous_settings and
        #      self.previous_settings.get('python_paths') != self.settings.get('python_paths'))
        # ):
        #     need_relint = True
        #     self.changeset.discard('python_paths')
        #     python_paths = self.settings.get('python_paths', {}).get(sublime.platform(), [])

        #     for path in python_paths:
        #         if path not in sys.path:
        #             sys.path.append(path)

        # If the syntax map changed, reassign linters to all views

        # if (
        #     'syntax_map' in self.changeset or
        #     (self.previous_settings and
        #      self.previous_settings.get('syntax_map') != self.settings.get('syntax_map'))
        # ):
        #     need_refetch = True
        #     self.changeset.discard('syntax_map')
        #     Linter.clear_all()
        #     util.apply_to_all_views(lambda view: Linter.assign(view, reset=True))

        # if (
        #     'no_column_highlights_line' in self.changeset or
        #     self.previous_settings.get('no_column_highlights_line') != self.settings.get('no_column_highlights_line')
        # ):
        #     need_relint = True
        #     self.changeset.discard('no_column_highlights_line')

        # if (
        #     'gutter_theme' in self.changeset or
        #     self.previous_settings.get('gutter_theme') != self.settings.get('gutter_theme')
        # ):
        #     self.changeset.discard('gutter_theme')
        #     self.update_gutter_marks()

        # error_color = self.settings.get('error_color', '')
        # warning_color = self.settings.get('warning_color', '')

        # if (
        #     ('error_color' in self.changeset or 'warning_color' in self.changeset) or
        #     (self.previous_settings and error_color and warning_color and
        #      (self.previous_settings.get('error_color') != error_color or
        #       self.previous_settings.get('warning_color') != warning_color))
        # ):
        #     self.changeset.discard('error_color')
        #     self.changeset.discard('warning_color')

        #     if (
        #         sublime.ok_cancel_dialog(
        #             'You changed the error and/or warning color. '
        #             'Would you like to update the user color schemes '
        #             'with the new colors?')
        #     ):
        #         util.change_mark_colors(error_color, warning_color)

        # If any other settings changed, relint
        if (self.previous_settings or len(self.changeset) > 0):
            need_refetch = True

        self.changeset.clear()

        if need_refetch:
            SublimeBump.log_version_for_active_view()

        if self.previous_settings and self.on_update_callback:
            self.on_update_callback(need_relint)

    def save(self, view=None):
        """
        Regenerate and save the user settings.

        User settings are updated with the default settings and the defaults
        from every linter, and if the user settings are currently being edited,
        the view is updated.

        """

        self.load()

        # Fill in default linter settings
        settings = self.settings

        filename = 'SublimeBump.sublime-settings'
        user_prefs_path = os.path.join(sublime.packages_path(), 'User', filename)
        settings_views = []

        if view is None:
            # See if any open views are the user prefs
            for window in sublime.windows():
                for view in window.views():
                    if view.file_name() == user_prefs_path:
                        settings_views.append(view)
        else:
            settings_views = [view]

        if settings_views:
            def replace(edit):
                if not view.is_dirty():
                    j = json.dumps({'user': settings}, indent=4, sort_keys=True)
                    j = j.replace(' \n', '\n')
                    view.replace(edit, sublime.Region(0, view.size()), j)

            for view in settings_views:
                edits[view.id()].append(replace)
                view.run_command('sublimebump_edit')
                view.run_command('save')
        else:
            user_settings = sublime.load_settings('SublimeBump.sublime-settings')
            user_settings.set('user', settings)
            sublime.save_settings('SublimeBump.sublime-settings')

    def on_prefs_update(self):
        """Perform maintenance when the ST prefs are updated."""
        print('Updated')
        #util.generate_color_scheme()


if 'plugin_is_loaded' not in globals():
    settings = Settings()

    plugin_is_loaded = False

def debug_mode():
    return settings.get('debug')

def edit(vid, edit):
    """Perform an operation on a view with the given edit object."""
    callbacks = edits.pop(vid, [])

    for c in callbacks:
        c(edit)
