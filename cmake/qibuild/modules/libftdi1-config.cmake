## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(LIBFTDI1)

fpath(LIBFTDI1 libftdi1/ftdi.h)
flib(LIBFTDI1 ftdi1)

export_lib(LIBFTDI1)
