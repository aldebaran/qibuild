## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OPENCV2_VIDEO)
fpath(OPENCV2_VIDEO opencv2/video/video.hpp)
flib(OPENCV2_VIDEO OPTIMIZED NAMES opencv_video)
flib(OPENCV2_VIDEO DEBUG     NAMES opencv_video)
export_lib(OPENCV2_VIDEO)
