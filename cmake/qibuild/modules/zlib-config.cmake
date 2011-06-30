## Copyright (C) 2011 Aldebaran Robotics

#this is zlib for windows
clean(ZLIB)
fpath(ZLIB zlib.h PATH_SUFFIXES zlib)
if (UNIX AND NOT APPLE)
  set(ZLIB_LIBRARIES "-lz"  CACHE STRING "" FORCE)
else()
  flib(ZLIB OPTIMIZED zlib z)
  flib(ZLIB DEBUG NAMES zlib_d zlib z)
endif()
export_lib(ZLIB)

