## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(SNDFILE)
fpath(SNDFILE sndfile.h)
flib(SNDFILE sndfile libsndfile-1)
export_lib(SNDFILE)
