dependency_fields = [
    'dependencies',
    'devDependencies',
    'peerDependencies',
    'optionalDependencies',
]
supported_filenames = ['package.json']
default_registry = 'https://registry.npmjs.org';

default_distribution_mode = 'latest' # could be next
VERSION_MODES = (
    ('latest', 'Show released versions only'),
    ('next', 'Show upcoming (alpha, beta) versions')
)
default_tooltip = False
tooltip_styles = {
    'version_color': '#FFFFFF',
    'package_color': '#76C1BA',
    'background': '#253238'
};

def get_registry():
    return default_registry

def get_distribution_mode():
    return default_distribution_mode

def get_dependency_fields():
    return dependency_fields

def get_supported_filenames():
    return supported_filenames

def get_tooltip():
    return default_tooltip

def get_tooltip_styles():
    return tooltip_styles
