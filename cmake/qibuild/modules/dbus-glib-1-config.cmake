## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(DBUS-GLIB-1)
find_package(PkgConfig)
pkg_check_modules(DBUS-GLIB-1 dbus-glib-1)
export_lib_pkgconfig(DBUS-GLIB-1)
