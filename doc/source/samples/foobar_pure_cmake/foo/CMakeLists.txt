## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
include_directories("${CMAKE_SOURCE_DIR}/libbar")

add_executable(foo main.cpp)
target_link_libraries(foo bar)

install(TARGETS foo DESTINATION "bin")
