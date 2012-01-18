## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_TS)
fpath(OPENCV2_TS opencv2/ts/ts.hpp)
flib(OPENCV2_TS OPTIMIZED NAMES opencv_ts)
flib(OPENCV2_TS DEBUG     NAMES opencv_ts)
qi_set_global(OPENCV2_TS_DEPENDS "OPENCV2_CORE")
export_lib(OPENCV2_TS)
