## Copyright (C) 2011 Aldebaran Robotics

clean(GSTREAMER)
find_package(PkgConfig)
pkg_check_modules(GSTREAMER gstreamer-0.10)
export_lib_pkgconfig(GSTREAMER)
