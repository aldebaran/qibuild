## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_FEATURES2D)
fpath(OPENCV2_FEATURES2D opencv2/features2d/features2d.hpp)
flib(OPENCV2_FEATURES2D OPTIMIZED NAMES opencv_features2d)
flib(OPENCV2_FEATURES2D DEBUG     NAMES opencv_features2d)
qi_set_global(OPENCV2_FEATURES2D_DEPENDS "OPENCV2_CORE;OPENCV2_IMGPROC;OPENCV2_HIGHGUI;OPENCV2_FLANN")
export_lib(OPENCV2_FEATURES2D)
