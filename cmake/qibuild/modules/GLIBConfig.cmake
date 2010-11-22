## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(GLIB)

if(UNIX AND NOT APPLE)
  set(GLIB_IN_SYSTEM "SYSTEM")
else(UNIX AND NOT APPLE)
  set(GLIB_IN_SYSTEM "")
endif(UNIX AND NOT APPLE)

fpath(GLIB glib.h PATH_SUFFIXES glib-2.0 ${GLIB_IN_SYSTEM})

#glibconfig.h is located in the folder (at least on archlinux and gentoo)
if (UNIX AND NOT APPLE)
  set(GLIB_INCLUDE_DIR /usr/lib/glib-2.0/include ${GLIB_INCLUDE_DIR} CACHE PATH "" FORCE)
endif(UNIX AND NOT APPLE)

flib (GLIB glib-2.0     glib-2.0.0       ${GLIB_IN_SYSTEM})
flib (GLIB gobject-2.0  gobject-2.0.0    ${GLIB_IN_SYSTEM})
flib (GLIB gio-2.0      gio-2.0.0        ${GLIB_IN_SYSTEM})
flib (GLIB gthread-2.0  gthread-2.0.0    ${GLIB_IN_SYSTEM})
flib (GLIB gmodule-2.0  gmodule-2.0.0    ${GLIB_IN_SYSTEM})

export_lib(GLIB)
