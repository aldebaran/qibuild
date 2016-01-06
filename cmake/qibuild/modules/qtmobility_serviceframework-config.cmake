## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(QTMOBILITY_SERVICEFRAMEWORK)
fpath(QTMOBILITY_SERVICEFRAMEWORK qservicemanager.h PATH_SUFFIXES QtServiceFramework)
fpath(QTMOBILITY_SERVICEFRAMEWORK QServiceManager PATH_SUFFIXES QtServiceFramework)
fpath(QTMOBILITY_SERVICEFRAMEWORK qmobilityglobal.h PATH_SUFFIXES QtMobility)
flib(QTMOBILITY_SERVICEFRAMEWORK QtServiceFramework)
export_lib(QTMOBILITY_SERVICEFRAMEWORK)
