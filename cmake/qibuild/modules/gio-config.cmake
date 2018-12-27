## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

find_package(PkgConfig)
if(UNIX AND NOT APPLE)
  pkg_check_modules(GIO gio-unix-2.0)
  if(NOT GIO_FOUND)
    pkg_check_modules(GIO gio-2.0)
  endif()
else()
  pkg_check_modules(GIO gio-2.0)
endif()
export_lib_pkgconfig(GIO)
