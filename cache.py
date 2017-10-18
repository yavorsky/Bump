versions = {}

def get_by_vid(vid):
  return versions[vid]

def get_by_package(package, version_mode, vid):
  if not in_cache(package, version_mode, vid):
      return None
  return versions[vid][package + version_mode]

def in_cache(package, version_mode, vid):
  package_str = package + version_mode
  return vid in versions and package_str in versions[vid]

def set_package(package, version_mode, vid, version):
  if (vid not in versions): versions[vid] = {}
  versions[vid][package + version_mode] = version
