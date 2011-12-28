## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)
project(world)
find_package(qibuild)

include_directories(".")

qi_create_lib(world SHARED
  world/world.h
  world/world.cpp)

qi_create_lib(bar STATIC INTERNAL
  bar/bar.h
  bar/bar.cpp)

qi_create_lib(myplugin SHARED SUBFOLDER "word"
  plugin.cpp
  plugin.h)


qi_install_header(world/world.h SUBFOLDER world)
qi_install_header(bar/bar.h KEEP_RELATIVE_PATHS)

qi_stage_lib(world)
qi_stage_lib(bar)

qi_stage_cmake(cmake/foo-config.cmake)

find_package(foo REQUIRED)
foo()
