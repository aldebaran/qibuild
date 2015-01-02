## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(cross C)

add_library(foo SHARED foo.c)
add_library(bar SHARED bar.c)

target_link_libraries(bar foo)
install(TARGETS bar
  DESTINATION lib)
