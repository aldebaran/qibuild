## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(GSOAP)
fpath(GSOAP stdsoap2.h PATH_SUFFIXES gsoap)
flib(GSOAP gsoap)
export_lib(GSOAP)
