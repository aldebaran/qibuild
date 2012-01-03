## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(GETTEXT)

if(NOT WIN32)
  set(GETTEXT_DEPENDS DL)
endif()
fpath(GETTEXT libintl.h)

#dont find libintl on linux => libintl is part of glibc
if (NOT UNIX OR APPLE)
  flib(GETTEXT NAMES intl libintl intl.8.0.2)
endif()

if (NOT WIN32)
  flib(GETTEXT NAMES gettextpo gettextpo.0 gettextpo.0.4.0)
  flib(GETTEXT gettextsrc  gettextsrc-0.17)
  flib(GETTEXT gettextlib  gettextlib-0.17)
endif()

export_lib(GETTEXT)
