##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics

#this is zlib for windows



clean(ZLIB)
fpath(ZLIB zlib.h PATH_SUFFIXES zlib)

flib(ZLIB OPTIMIZED zlib z)
flib(ZLIB DEBUG NAMES zlib_d zlib z)

export_lib(ZLIB)

