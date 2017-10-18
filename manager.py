import enum

dependency_fields = [
    'dependencies',
    'devDependencies',
    'peerDependencies'
]
supported_filenames = ['package.json']
default_registry = 'https://registry.npmjs.org';

default_version = 'latest' # could be next

def get_registry():
    return default_registry

def get_package_version():
    return default_version

def get_dependency_fields():
    return dependency_fields

def get_supported_filenames():
    return supported_filenames
