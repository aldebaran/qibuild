## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# If someone is using qibuild configure, includes
# the dependencies.cmake file
if(EXISTS ${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake)
  include(${CMAKE_CURRENT_BINARY_DIR}/dependencies.cmake)
endif()

get_filename_component(_this_dir ${CMAKE_CURRENT_LIST_FILE} PATH)
set(_qibuild_path ${_this_dir}/..)

list(FIND CMAKE_MODULE_PATH "${_qibuild_path}" _found)
if(_found STREQUAL "-1")
  list(APPEND CMAKE_MODULE_PATH "${_qibuild_path}")
endif()
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} CACHE INTERNAL ""  FORCE)

include(${_this_dir}/general.cmake)

