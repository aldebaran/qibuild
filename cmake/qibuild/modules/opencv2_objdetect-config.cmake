## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_OBJDETECT)
fpath(OPENCV2_OBJDETECT opencv2/objdetect/objdetect.hpp)
flib(OPENCV2_OBJDETECT OPTIMIZED NAMES opencv_objdetect)
flib(OPENCV2_OBJDETECT DEBUG     NAMES opencv_objdetect)
qi_set_global(OPENCV2_OBJDETECT_DEPENDS "OPENCV2_CORE;OPENCV2_FEATURES2D")
export_lib(OPENCV2_OBJDETECT)
