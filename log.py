from string import Template
from . import settings as conf
from . import defaults
from . import Tooltip

def show_tooltip(view, package, version, has_matched = True):
    common_styles = defaults.get_tooltip_styles()
    tooltip_styles = conf.settings.get('tooltip_styles', {})

    for field in tooltip_styles:
      if field in common_styles:
          common_styles[field] = tooltip_styles[field]

    view.show_popup(Tooltip.get_str(has_matched).substitute(package=package, version=version, package_color=common_styles['package_color'], version_color=common_styles['version_color'], background=common_styles['background']), location=-1, max_width=400)

def log_version(view, package, version, has_matched, tooltip = False):
    formatted_post = ''
    if has_matched:
        formatted_post += ' ✓'
    formatted = Template('$package: $version' + formatted_post).substitute(package=package, version=version)
    update_log(view, formatted);
    if tooltip:
        show_tooltip(view, package, version, has_matched)

def update_log(view, text):
    unset_log(view)
    set_log(view, text)

def set_log(view, lineText):
    view.set_status('sublimebump', lineText)

def unset_log(view):
    view.erase_status('sublimebump')

def printf(*args):
  print('SublimeBump: ', end='')

  for arg in args:
      print(arg, end=' ')

  print()
