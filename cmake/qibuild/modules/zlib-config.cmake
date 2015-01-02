## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#this is zlib for windows
clean(ZLIB)
fpath(ZLIB zlib.h PATH_SUFFIXES zlib)
flib(ZLIB OPTIMIZED zlib z)
flib(ZLIB DEBUG NAMES zlib_d zlib z)
export_lib(ZLIB)

