## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(SOPRANO)
fpath(SOPRANO soprano/soprano.h)
flib(SOPRANO soprano)
flib(SOPRANO sopranoclient)
flib(SOPRANO sopranoserver)
qi_persistent_set(SOPRANO_DEPENDS QT5_DBUS)
export_lib(SOPRANO)
