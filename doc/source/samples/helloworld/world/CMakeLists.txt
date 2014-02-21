## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(world)
find_package(qibuild)

include_directories(".")

qi_create_lib(world SHARED
  world/world.hpp
  world/world.cpp)

qi_install_header(world/world.hpp SUBFOLDER world)

qi_stage_lib(world)
