## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(foo)
find_package(qibuild)

qi_create_lib(spam spam.cpp)
qi_stage_lib(spam)

qi_create_lib(eggs eggs.cpp)
qi_use_lib(eggs spam)
qi_stage_lib(eggs)

qi_create_lib(bar  bar.cpp)
qi_use_lib(bar eggs)
