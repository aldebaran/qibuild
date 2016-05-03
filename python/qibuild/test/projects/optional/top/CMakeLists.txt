## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(optional C)

find_package(qibuild)

qi_add_optional_package(foo)
if(NOT WITH_FOO)
  qi_error("WITH_FOO should be ON")
endif()

add_subdirectory(bin)
