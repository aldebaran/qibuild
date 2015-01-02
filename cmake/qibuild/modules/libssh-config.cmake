## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(LIBSSH)

fpath(LIBSSH libssh/libssh.h)
flib(LIBSSH ssh)

export_lib(LIBSSH)
