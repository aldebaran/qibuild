## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_FLANN)
fpath(OPENCV2_FLANN opencv2/flann/flann.hpp)
flib(OPENCV2_FLANN OPTIMIZED NAMES opencv_flann)
flib(OPENCV2_FLANN DEBUG     NAMES opencv_flann)
qi_set_global(OPENCV2_FLANN_DEPENDS "OPENCV2_CORE")
export_lib(OPENCV2_FLANN)
