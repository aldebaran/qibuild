## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


project(FooLib)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
qi_create_lib(foolib foo/hello.hpp foo/hello.cpp)
qi_install_header(foo/hello.hpp SUBFOLDER foo)
qi_stage_lib(foolib)
