## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

if(NOT PROJECT_NAME)
  message(FATAL_ERROR "Please call find_package(qibuild) after project()")
endif()

# If someone is using qibuild configure, includes
# the dependencies.cmake file
if(EXISTS ${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake)
  include(${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake)
endif()

# remove qi_tests.json
# Note:
#  this will fail silently if the file does not exist
#  this file is used by `qitest run` and other commands
#  later on and can be patched from CMake
file(REMOVE ${CMAKE_CURRENT_BINARY_DIR}/qitest.cmake)

get_filename_component(_this_dir ${CMAKE_CURRENT_LIST_FILE} PATH)
set(_qibuild_path ${_this_dir}/..)

list(FIND CMAKE_MODULE_PATH "${_qibuild_path}" _found)
if(_found STREQUAL "-1")
  list(APPEND CMAKE_MODULE_PATH "${_qibuild_path}")
endif()
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} CACHE INTERNAL ""  FORCE)

# So that find_package(qibuild) works:
set(qibuild_DIR ${_this_dir} CACHE INTERNAL "" FORCE)
include(${_this_dir}/general.cmake)

# Make sure *-config.cmake files are found first in toolchain packages,
# then in qibuild/cmake/modules
qi_persistent_append_uniq(CMAKE_PREFIX_PATH "${_this_dir}/modules/")
