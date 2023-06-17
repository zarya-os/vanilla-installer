pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
defaultsdir = join_paths(pkgdatadir, 'vanilla_installer/defaults')

sources = [
  '__init__.py',
  'language.py',
  'keyboard.py',
  'disk.py',
  'welcome.py',
]

install_data(sources, install_dir: defaultsdir)
