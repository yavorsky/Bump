import re
import sublime

lineRe = r'"\s?(.+)\s?"\s?:?\s?"(.+)"'

def get_current_package(text):
    groups = re.search(lineRe, text)
    return [groups.group(1), groups.group(2)]

def get_current_package_coords(text):
    groups = re.search(lineRe, text)
    return [groups.span(1), groups.span(2)]

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
