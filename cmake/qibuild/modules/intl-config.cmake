## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


if(NOT WIN32)
  set(INTL_DEPENDS DL)
endif()

if(APPLE)
  # Use homebrew installation path
  fpath(INTL libintl.h HINTS /usr/local/opt/gettext/include/)
else()
  fpath(INTL libintl.h)
endif()

if(UNIX AND NOT APPLE)
  # on linux, libintl is part of glibc
  export_header(INTL)
  return()
endif()

if(APPLE)
  # Use homebrew installation path
  flib(INTL NAMES intl HINTS /usr/local/opt/gettext/lib/)
  export_lib(INTL)
endif()
