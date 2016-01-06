## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(SQLITE3)

fpath(SQLITE3 sqlite3.h)
flib(SQLITE3  sqlite3)

if(UNIX AND NOT APPLE)
  qi_persistent_set(SQLITE3_DEPENDS PTHREAD DL)
else()
  qi_persistent_set(SQLITE3_DEPENDS PTHREAD)
endif()
export_lib(SQLITE3)
