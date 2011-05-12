## Copyright (C) 2011 Aldebaran Robotics

clean(ARCHIVE)
fpath(ARCHIVE archive.h PATH_SUFFIXES archive)

flib(ARCHIVE NAMES archive)

if (APPLE)
  set(ARCHIVE_DEPENDS "ZLIB")
endif()

export_lib(ARCHIVE)

