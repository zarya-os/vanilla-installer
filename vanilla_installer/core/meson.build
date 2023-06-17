pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
coredir = join_paths(pkgdatadir, 'vanilla_installer/core')

sources = [
  '__init__.py',
  'languages.py',
  'keymaps.py',
  'disks.py',
  'system.py'
]

install_data(sources, install_dir: coredir)
