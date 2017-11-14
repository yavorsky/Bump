import os
import json
from string import Template
from urllib import request
from urllib.parse import urljoin
from . import settings as conf

from . import defaults

def get_request(pathname):
    webURL = request.urlopen(pathname)
    data = webURL.read()
    encoding = webURL.info().get_content_charset('utf-8')
    return json.loads(data.decode(encoding))

def fetch_package_version(package, version, callback = None):
    registry = conf.settings.get('registry', defaults.get_registry())
    pathname = urljoin(registry, package.replace('/', '%2F'))
    pathname = Template('$pathname?version=$version').substitute(pathname=pathname, version=version)
    response = get_request(pathname)
    if (callback):
        callback(response['version'])
