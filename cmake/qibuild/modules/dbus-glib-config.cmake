## Copyright (C) 2011 Aldebaran Robotics

clean(DBUS-GLIB)
find_package(PkgConfig)
pkg_check_modules(DBUS-GLIB dbus-glib-1)
export_lib_pkgconfig(DBUS-GLIB)
