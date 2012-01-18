## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_ML)
fpath(OPENCV2_ML opencv2/ml/ml.hpp)
flib(OPENCV2_ML OPTIMIZED NAMES opencv_ml)
flib(OPENCV2_ML DEBUG     NAMES opencv_ml)
qi_set_global(OPENCV2_ML_DEPENDS "OPENCV2_CORE")
export_lib(OPENCV2_ML)
