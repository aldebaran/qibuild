## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(test_uselib C)

find_package(qibuild)
include_directories(".")

qi_create_lib(a a.c)
qi_stage_lib(a)

qi_create_lib(b b.c)
qi_stage_lib(b)

qi_create_lib(cc cc.c)
qi_stage_lib(cc)

qi_create_lib(d d.c)
qi_use_lib(d a)
qi_use_lib(d b)
qi_stage_lib(d)

qi_create_bin(e e.c)
qi_use_lib(e d cc)

if(SHOULD_FAIL)
  qi_create_lib("invalid@name" e.c)
  qi_use_lib("invalid@name" d)
endif()
