## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(test_stage_lib C)

find_package(qibuild)
include_directories(".")

if(SHOULD_FAIL_STAGE_LIB_BUT_REALLY_BIN)
  qi_create_bin(foo foo.c)
  qi_stage_lib(foo)
endif()

if(SHOULD_FAIL_STAGE_NO_SUCH_TARGET)
  qi_stage_lib(foo)
endif()
