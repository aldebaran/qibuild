## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_CALIB3D)
fpath(OPENCV2_CALIB3D opencv2/calib3d/calib3d.hpp)
flib(OPENCV2_CALIB3D OPTIMIZED NAMES opencv_calib3d)
flib(OPENCV2_CALIB3D DEBUG     NAMES opencv_calib3d)
export_lib(OPENCV2_CALIB3D)
