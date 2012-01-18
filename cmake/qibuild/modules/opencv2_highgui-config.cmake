## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_HIGHGUI)
fpath(OPENCV2_HIGHGUI opencv2/highgui/highgui.hpp)
flib(OPENCV2_HIGHGUI OPTIMIZED NAMES opencv_highgui)
flib(OPENCV2_HIGHGUI DEBUG     NAMES opencv_highgui)
qi_set_global(OPENCV2_HIGHGUI_DEPENDS "OPENCV2_CORE")
export_lib(OPENCV2_HIGHGUI)
