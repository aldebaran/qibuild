## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

find_package(PkgConfig)
pkg_check_modules(GSTREAMER gstreamer-0.10)
export_lib_pkgconfig(GSTREAMER)
