## Copyright (C) 2011 Aldebaran Robotics

clean(DBUS)
find_package(PkgConfig)
pkg_check_modules(DBUS dbus-1)
export_lib_pkgconfig(DBUS)
