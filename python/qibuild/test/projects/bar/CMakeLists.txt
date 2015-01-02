## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(bar)

find_package(qibuild)

find_package(footool)

configure_file(run_foo_tool.in.cmake
 ${CMAKE_CURRENT_BINARY_DIR}/run_foo_tool.cmake)

install(SCRIPT
 ${CMAKE_CURRENT_BINARY_DIR}/run_foo_tool.cmake)

install(FILES ${CMAKE_CURRENT_BINARY_DIR}/foo.out
  DESTINATION "share/foo"
  COMPONENT data)
