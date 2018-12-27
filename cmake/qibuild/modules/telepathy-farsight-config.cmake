## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(TELEPATHY-FARSIGHT)
fpath(TELEPATHY-FARSIGHT telepathy-glib/telepathy-glib.h PATH_SUFFIXES telepathy-1.0)
flib(TELEPATHY-FARSIGHT telepathy-farsight)
qi_persistent_set(TELEPATHY-FARSIGHT_DEPENDS
  TELEPATHY-GLIB
  GSTREAMER-FARSIGHT
  DBUS-GLIB-1)
export_lib(TELEPATHY-FARSIGHT)
