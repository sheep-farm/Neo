project('neo',
  version: '0.1.0',
  meson_version: '>= 0.59.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')
fs = import('fs')

py_installation = python.find_installation('python3')

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'neo')

conf = configuration_data()
conf.set('PYTHON', py_installation.full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

# Instalar wheels do Scrapy
wheels_file = join_paths(meson.current_source_dir(), 'wheels_list.txt')
if fs.exists(wheels_file)
  wheels_content = fs.read(wheels_file)
  wheels_raw = wheels_content.strip().replace('\'', '').replace(',', '')
  wheels = wheels_raw.split()

  wheels_dir = join_paths(meson.current_source_dir(), 'wheels')
  wheel_paths = []

  foreach w : wheels
    wheel_paths += [join_paths(wheels_dir, w)]
  endforeach

  wheels_str = ' '.join(wheel_paths)

  # Script de instalação dos wheels
  meson.add_install_script(
    'sh', '-c',
    'pip3 install --upgrade --no-deps --target="$MESON_INSTALL_DESTDIR_PREFIX/lib/python3.12/site-packages" --no-cache-dir ' + wheels_str + ' && ' +
    'find "$MESON_INSTALL_DESTDIR_PREFIX" -type d -name tests -exec rm -rf {} + || true'
  )
endif

subdir('data')
subdir('src')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)