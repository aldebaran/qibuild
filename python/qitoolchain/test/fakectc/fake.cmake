## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
set(CMAKE_CROSSCOMPILING ON)

include(CMakeForceCompiler)
CMAKE_FORCE_C_COMPILER("${CMAKE_CURRENT_LIST_DIR}/fake-gcc" GNU)
CMAKE_FORCE_CXX_COMPILER("${CMAKE_CURRENT_LIST_DIR}/fake-g++" GNU)
set(CMAKE_LINKER  "${CMAKE_CURRENT_LIST_DIR}/fake-ld"     CACHE FILEPATH "" FORCE)
set(CMAKE_AR      "${CMAKE_CURRENT_LIST_DIR}/fake-ar"     CACHE FILEPATH "" FORCE)
set(CMAKE_RANLIB  "${CMAKE_CURRENT_LIST_DIR}/fake-ranlib" CACHE FILEPATH "" FORCE)

set(CMAKE_CROSSCOMPILING ON)
# So that APPLE does not get defined and we don't try to run
# install_name_tool on fake binaries
set(CMAKE_SYSTEM_NAME "Linux")
set(CMAKE_EXECUTABLE_FORMAT "ELF")
