from string import Template

def get_str():
    return Template('<style>html { background-color: $background; margin: 0px; } body { margin: 5px; } div { margin: 0px; word-wrap:break-word; } .line { margin: 4px 5px; font-size: 13px; } .package { color: $package_color; } .version { color: $version_color }</style><div><p class="line"><span class="package">$package: </span><span class="version"> $version</span></p></div>')
