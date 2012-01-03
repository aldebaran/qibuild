## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_CORE)
fpath(OPENCV2_CORE opencv2/core/core.hpp)
flib(OPENCV2_CORE OPTIMIZED NAMES opencv_core)
flib(OPENCV2_CORE DEBUG     NAMES opencv_core)
export_lib(OPENCV2_CORE)
