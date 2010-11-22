##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

if(UNIX AND NOT APPLE)
  set(IN_SYSTEM "SYSTEM")
else(UNIX AND NOT APPLE)
  set(IN_SYSTEM "")
endif(UNIX AND NOT APPLE)

clean(GSTREAMER)
fpath(GSTREAMER  gst/gst.h PATH_SUFFIXES gstreamer-0.10 gstreamer ${IN_SYSTEM})
flib (GSTREAMER  NAMES
  gstreamer-0.10.0
  gstreamer-0.10
  gstreamer
  ${IN_SYSTEM})

if (APPLE)
  depend (GSTREAMER REQUIRED ICONV)
  depend (GSTREAMER REQUIRED GETTEXT)
endif (APPLE)

export_lib(GSTREAMER)
