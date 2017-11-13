import re
import sublime

lineRe = r'"\s?(.+)\s?"\s?:?\s?"(.+)?"'
lineReWithoutVersion = r'"\s?(.+)\s?"\s?:?\s?("")'

def get_current_package(text):
    groups = re.search(lineRe, text)
    if not groups:
        return [None, None]

    return [groups.group(1), groups.group(2) or '']

def get_current_package_coords(text):
    groups = re.search(lineRe, text)
    if not groups:
        return [None, None]
    name_coords = groups.span(1)
    version_coords = groups.span(2)
    if not version_coords or version_coords[0] is -1:
        empty_version_groups = re.search(lineReWithoutVersion, text)
        if not empty_version_groups:
            return [None, None]
        version_spans = empty_version_groups.span(2)
        version_coords = [version_spans[0] + 1, version_spans[1] + 1]
    return [name_coords, version_coords]

def get_text(view):
    return view.substr(sublime.Region(0, view.size()))

def get_parent_key(view, region):
    text = view.substr(sublime.Region(0, region.begin()))
    open_pos = text.rfind('{')
    close_pos = text.rfind('}')

    if close_pos > open_pos:
        return None

    upper_field_re = r'"\s?(.+)\s?"\s?:\s?{'
    parent_keys = re.findall(upper_field_re, text)

    if not len(parent_keys):
        return None
    return parent_keys[-1];

def get_active_region(view):
    try:
        selection = view.sel()
        region = selection[0]
    except IndexError:
        region = None
    return region

def get_text_from_line(view, region):
    try:
        line_text = view.substr(view.line(region)).strip()
    except IndexError:
        line_text = None
    return line_text
