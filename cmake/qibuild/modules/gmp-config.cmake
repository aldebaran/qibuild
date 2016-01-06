## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(GMP)

fpath(GMP gmp.h)
flib(GMP NAMES gmp)
export_lib(GMP)
