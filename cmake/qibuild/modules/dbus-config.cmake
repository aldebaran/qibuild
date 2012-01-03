## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(DBUS)
find_package(PkgConfig)
pkg_check_modules(DBUS dbus-1)
export_lib_pkgconfig(DBUS)
