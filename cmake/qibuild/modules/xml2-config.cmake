## Copyright (C) 2011 Aldebaran Robotics

clean(XML2)
fpath(XML2 libxml/parser.h PATH_SUFFIXES libxml2)
flib(XML2 xml2)
if (APPLE)
  set(XML2_DEPENDS ZLIB)
endif()
export_lib(XML2)
