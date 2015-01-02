## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(foo)
find_package(qibuild)

enable_testing()


set(ANSWER 42)
qi_create_config_h(_out ${CMAKE_CURRENT_SOURCE_DIR}/config.in.h foo/config.h)
qi_create_bin(foo main.cpp)
message(STATUS "_out: ${_out}")

if(WITH_EXTRA_INSTALL_RULE)
  qi_install_header(${_out} KEEP_RELATIVE_PATHS)
endif()
