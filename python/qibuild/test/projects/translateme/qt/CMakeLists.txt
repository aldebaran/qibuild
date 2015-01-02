## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(translateme-qt)
find_package(qibuild)

qi_create_bin(translateme main.cpp)
qi_use_lib(translateme QT_QTCORE QT_QTGUI)
