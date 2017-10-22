dependency_fields = [
    'dependencies',
    'devDependencies',
    'peerDependencies'
]
supported_filenames = ['package.json']
default_registry = 'https://registry.npmjs.org';

default_distribution_mode = 'latest' # could be next
VERSION_MODES = (
    ('latest', 'Show released versions only'),
    ('next', 'Show upcoming (alpha, beta) versions')
)

def get_registry():
    return default_registry

def get_distribution_mode():
    return default_distribution_mode

def get_dependency_fields():
    return dependency_fields

def get_supported_filenames():
    return supported_filenames
