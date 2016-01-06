## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(GCRYPT)

fpath(GCRYPT gcrypt.h)
flib(GCRYPT NAMES gcrypt)
export_lib(GCRYPT)
