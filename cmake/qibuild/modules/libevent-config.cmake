## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(LIBEVENT)

fpath(LIBEVENT event.h PATH_SUFFIXES event2)
flib(LIBEVENT NAMES event event_core)

export_lib(LIBEVENT)
