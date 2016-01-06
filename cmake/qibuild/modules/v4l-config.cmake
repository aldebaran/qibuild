## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(V4L)
fpath(V4L libv4l1.h)
fpath(V4L libv4l2.h)

flib(V4L NAMES v4l1)
flib(V4L NAMES v4l2)
flib(V4L NAMES v4lconvert)
export_lib(V4L)

