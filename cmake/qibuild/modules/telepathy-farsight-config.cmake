## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(TELEPATHY-FARSIGHT)
fpath(TELEPATHY-FARSIGHT telepathy-glib/telepathy-glib.h PATH_SUFFIXES telepathy-1.0)
flib(TELEPATHY-FARSIGHT telepathy-farsight)
export_lib(TELEPATHY-FARSIGHT)
