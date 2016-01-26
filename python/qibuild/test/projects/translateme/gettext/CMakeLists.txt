## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(translate)
find_package(qibuild)

qi_create_bin(translate main.cpp)

find_package(intl NO_MODULE)

if(INTL_PACKAGE_FOUND)
  add_definitions("-DWITH_INTL")
  qi_use_lib(translate INTL)
  qi_create_trad(translate "po")
endif()
