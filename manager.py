dependency_fields = [
    'dependencies',
    'devDependencies',
    'peerDependencies'
]
supported_filenames = ['package.json']
default_registry = 'https://registry.npmjs.org';

default_version = 'latest' # could be next
VERSION_MODES = (
    ('latest', 'Show latest released versions'),
    ('next', 'Show upcoming (alpha, beta) versions')
)

def get_registry():
    return default_registry

def get_package_version():
    return default_version

def set_package_version(version):
    default_version = version

def get_dependency_fields():
    return dependency_fields

def get_supported_filenames():
    return supported_filenames
