## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_LEGACY)
fpath(OPENCV2_LEGACY opencv2/legacy/legacy.hpp)
flib(OPENCV2_LEGACY OPTIMIZED NAMES opencv_legacy)
flib(OPENCV2_LEGACY DEBUG     NAMES opencv_legacy)
qi_set_global(OPENCV2_LEGACY_DEPENDS "OPENCV2_CORE;OPENCV2_IMGPROC;OPENCV2_FEATURES2D;OPENCV2_CALIB3D")
export_lib(OPENCV2_LEGACY)
