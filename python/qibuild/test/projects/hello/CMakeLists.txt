## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)
project(hello)
find_package(qibuild)
find_package(bar)
message(STATUS "bar_FOUND: ${bar_FOUND}")

qi_create_bin(hello "main.cpp")
qi_use_lib(hello world)
if("${WORLD_OK}" STREQUAL "TRUE")
  qi_info("The world is OK")
else()
  qi_error("WORLD_OK should be set")
endif()

# Add a test that just runs hello without arguments
qi_add_test(zero_test hello)

# Use the foo file staged by world:
find_package(foo REQUIRED)
foo()
