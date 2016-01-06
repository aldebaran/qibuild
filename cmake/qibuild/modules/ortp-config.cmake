## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(ORTP)
fpath(ORTP "ortp.h" PATH_SUFFIXES "ortp")
flib(ORTP "ortp" NAMES ortp)
export_lib(ORTP)
