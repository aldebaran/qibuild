## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PTHREAD)
fpath(PTHREAD "pthread.h")
flib(PTHREAD pthread pthreadVCE2)
export_lib(PTHREAD)
