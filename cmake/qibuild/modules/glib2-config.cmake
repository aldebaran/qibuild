## Copyright (C) 2011 Aldebaran Robotics

clean(GLIB2)

find_package(PkgConfig)
pkg_check_modules(GLIB2 glib-2.0)
qi_set_cache(GLIB2_INCLUDE_DIR "${GLIB_INCLUDE_DIRS}")

export_lib(GLIB2)
