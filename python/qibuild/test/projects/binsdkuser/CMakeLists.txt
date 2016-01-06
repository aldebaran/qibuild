## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(binsdkuser)

find_package(qibuild)

find_package(FOO)
if(NOT EXISTS ${FOO_LIBRARIES})
  qi_error("FOO_LIBRARIES: ${FOO_LIBRARIES} does not exist")
endif()
