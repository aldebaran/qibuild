##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

if(UNIX AND NOT APPLE)
  set(IN_SYSTEM "SYSTEM")
else(UNIX AND NOT APPLE)
  set(IN_SYSTEM "")
endif(UNIX AND NOT APPLE)

clean(XML2)
fpath(XML2 libxml/parser.h PATH_SUFFIXES libxml2 ${IN_SYSTEM})
flib(XML2 xml2 ${IN_SYSTEM})
if (TARGET_HOST STREQUAL "TARGET_HOST_MACOSX")
  depend(XML2 REQUIRED ZLIB)
endif (TARGET_HOST STREQUAL "TARGET_HOST_MACOSX")
export_lib(XML2)
