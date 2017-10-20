from string import Template

def log_version(view, package, version):
    formatted = Template('$package: $version').substitute(package=package, version=version)
    update_log(view, formatted);

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
