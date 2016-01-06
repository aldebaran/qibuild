## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(LIBTOOL)
fpath(LIBTOOL ltdl.h.h)
fpath(LIBTOOL libltdl/lt_system.h)
flib(LIBTOOL NAMES ltdl)
export_lib(LIBTOOL)

