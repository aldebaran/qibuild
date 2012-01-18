## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_CONTRIB)
fpath(OPENCV2_CONTRIB opencv2/contrib/contrib.hpp)
flib(OPENCV2_CONTRIB OPTIMIZED NAMES opencv_contrib)
flib(OPENCV2_CONTRIB DEBUG     NAMES opencv_contrib)
qi_set_global(OPENCV2_CONTRIB_DEPENDS "OPENCV2_CORE;OPENCV2_FEATURES2D;OPENCV2_OBJDETECT")
export_lib(OPENCV2_CONTRIB)
