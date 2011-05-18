## Copyright (C) 2011 Aldebaran Robotics

clean(GLIB2)
find_package(PkgConfig)
pkg_check_modules(GLIB2 glib-2.0)
export_lib_pkgconfig(GLIB2)
