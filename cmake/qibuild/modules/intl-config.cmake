## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


if(NOT WIN32)
  set(INTL_DEPENDS DL)
endif()
fpath(INTL libintl.h)

if(UNIX AND NOT APPLE)
  # on linux, libintl is part of glibc
  export_header(INTL)
  return()
endif()

if(APPLE)
  flib(INTL NAMES intl)
  export_lib(INTL)
endif()
