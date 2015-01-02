## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(GSTREAMER-FARSIGHT)
fpath(GSTREAMER-FARSIGHT gst/farsight/fs-plugin.h PATH_SUFFIXES gstreamer-0.10)
flib(GSTREAMER-FARSIGHT gstfarsight-0.10)
qi_persistent_set(GSTREAMER-FARSIGHT_DEPENDS GSTREAMER)
export_lib(GSTREAMER-FARSIGHT)
