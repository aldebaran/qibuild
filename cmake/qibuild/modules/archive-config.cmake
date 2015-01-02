## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(ARCHIVE)
fpath(ARCHIVE archive.h PATH_SUFFIXES archive)

flib(ARCHIVE NAMES archive)
qi_persistent_set(ARCHIVE_DEPENDS "ZLIB")
export_lib(ARCHIVE)

