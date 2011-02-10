## Copyright (C) 2011 Aldebaran Robotics



if(UNIX AND NOT APPLE)
  set(IN_SYSTEM "SYSTEM")
else()
  set(IN_SYSTEM "")
endif()

clean(XML2)
fpath(XML2 libxml/parser.h PATH_SUFFIXES libxml2 ${IN_SYSTEM})
flib(XML2 xml2 ${IN_SYSTEM})
if (TARGET_HOST STREQUAL "TARGET_HOST_MACOSX")
  depend(XML2 REQUIRED ZLIB)
endif()
export_lib(XML2)
