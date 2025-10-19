pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'neo'
gnome = import('gnome')

gnome.compile_resources('neo',
  'neo.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'neo.in',
  output: 'neo',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

neo_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'neo_settings.py',
  'settings.py',
  'settings_dialog.py',
  'spider_dialog.py',
  'field_dialog.py',
]

install_data(neo_sources, install_dir: moduledir)
