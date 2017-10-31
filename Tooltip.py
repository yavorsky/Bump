from string import Template

def get_str(has_matched):
    matched_icon = ''
    if has_matched:
      matched_icon = '<span class="check-icon">✓</span>'
      matched_version = '<span class="version"> $version</span>'
    else:
      matched_version = '<a href="" class="version"> $version</a>'

    return Template('<style>html { background-color: $background; margin: 0px; } body { margin: 5px; } div { margin: 0px; word-wrap:break-word; } .line { margin: 4px 5px; font-size: 13px; } .package { color: $package_color; } .version { color: $version_color; text-decoration: none; } .check-icon { color: #B9DE82; padding-left: 5px; }</style><div><p class="line"><span class="package">$package: </span>' + matched_version + matched_icon + '</p></div>')
