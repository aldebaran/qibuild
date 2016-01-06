## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
include_directories(".")

qi_create_lib(bar
  bar/bar.hpp
  bar/bar.cpp)

qi_stage_lib(bar)

qi_install_header(bar/bar.hpp
  SUBFOLDER bar)
