## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)
project(hello)
find_package(qibuild)
find_package(bar)
message(STATUS "bar_FOUND: ${bar_FOUND}")

qi_create_bin(hello "main.cpp")
qi_use_lib(hello world)

enable_testing()
# Add a test that just runs hello without arguments
qi_add_test(zero_test hello)

# Use the foo file staged by world:
find_package(foo REQUIRED)
foo()
