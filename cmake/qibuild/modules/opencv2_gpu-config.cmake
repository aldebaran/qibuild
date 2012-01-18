## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_GPU)
fpath(OPENCV2_GPU opencv2/gpu/gpu.hpp)
flib(OPENCV2_GPU OPTIMIZED NAMES opencv_gpu)
flib(OPENCV2_GPU DEBUG     NAMES opencv_gpu)
qi_set_global(OPENCV2_GPU_DEPENDS "OPENCV2_CORE;OPENCV2_IMGPROC;OPENCV2_OBJDETECT;OPENCV2_FEATURES2D")
export_lib(OPENCV2_GPU)
