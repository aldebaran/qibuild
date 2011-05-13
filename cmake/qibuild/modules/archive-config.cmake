## Copyright (C) 2011 Aldebaran Robotics

clean(ARCHIVE)
fpath(ARCHIVE archive.h PATH_SUFFIXES archive)

flib(ARCHIVE NAMES archive)
qi_set_global(ARCHIVE_DEPENDS "ZLIB")
export_lib(ARCHIVE)

