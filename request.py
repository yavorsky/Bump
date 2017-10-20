import os
import json
from string import Template
from urllib import request

from . import manager

def get_request(pathname):
    webURL = request.urlopen(pathname)
    data = webURL.read()
    encoding = webURL.info().get_content_charset('utf-8')
    return json.loads(data.decode(encoding))

def fetch_package_version(package, version, callback = None):
    registry = manager.get_registry()
    pathname = os.path.join(registry, package)
    pathname = Template('$pathname?version=$version').substitute(pathname=pathname, version=version)
    response = get_request(pathname)
    if (callback):
        callback(response['version'])
