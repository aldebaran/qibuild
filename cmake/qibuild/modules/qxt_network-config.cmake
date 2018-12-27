## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(QXT_NETWORK)
fpath(QXT_NETWORK qxtnetwork.h PATH_SUFFIXES qxt/QxtNetwork QxtNetwork)
fpath(QXT_NETWORK QxtNetwork PATH_SUFFIXES qxt)
flib(QXT_NETWORK QxtNetwork)
export_lib(QXT_NETWORK)
qi_persistent_set(QXT_NETWORK_DEPENDS "QXT_CORE" "QT_QTNETWORK")
