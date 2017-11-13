import sublime
import sublime_plugin

from . import parser

def format_version_on_line(view, edit, region, version):
  line_content = view.line(region)
  line_text = view.substr(line_content)
  [package_name, prev_version] = parser.get_current_package(line_text)
  [package_coords, version_coords] = parser.get_current_package_coords(line_text)
  [version_start, version_end] = version_coords
  line_content.a += version_start
  version_len = len(version)
  diff = version_len - len(prev_version)
  line_content.b = line_content.a + version_len - diff
  view.replace(edit, line_content, version)
