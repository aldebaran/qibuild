## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(RAPTOR)

fpath(RAPTOR raptor2/raptor2.h)
flib(RAPTOR NAMES raptor2)
export_lib(RAPTOR)
