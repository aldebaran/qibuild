## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(AVAHI)
fpath(AVAHI avahi-client/client.h PATH_SUFFIXES avahi)
flib(AVAHI avahi-common)
flib(AVAHI avahi-client)
export_lib(AVAHI)
