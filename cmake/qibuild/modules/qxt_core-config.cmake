## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(QXT_CORE)
fpath(QXT_CORE qxtcore.h PATH_SUFFIXES QxtCore qxt/QxtCore)
fpath(QXT_CORE QxtCore PATH_SUFFIXES qxt)
flib(QXT_CORE QxtCore)
export_lib(QXT_CORE)
qi_persistent_set(QXT_CORE_DEPENDS "QT_QTCORE")
