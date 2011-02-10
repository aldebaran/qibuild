## Copyright (C) 2011 Aldebaran Robotics

clean(ARCHIVE)
fpath(ARCHIVE archive.h PATH_SUFFIXES archive)

if(WIN32)
  flib(ARCHIVE OPTIMIZED NAMES archive)
  flib(ARCHIVE DEBUG     NAMES archive_d)
else()
  flib(ARCHIVE NAMES archive)
endif()

if (APPLE)
  set(ARCHIVE_DEPENDS "ZLIB")
endif()

export_lib(ARCHIVE)

