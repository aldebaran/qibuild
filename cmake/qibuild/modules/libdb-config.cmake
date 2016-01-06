## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(LIBDB)
fpath(LIBDB db.h PATH_SUFFIXES db4.8)

flib(LIBDB NAMES db-4.8)
export_lib(LIBDB)


