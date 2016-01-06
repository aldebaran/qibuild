## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

boost_flib("thread")
set(_deps)
if(UNIX)
  list(APPEND _deps PTHREAD)
endif()
#boost threads depends on chrono starting from version 1.50
if (Boost_VERSION GREATER "104900")
  list(APPEND _deps BOOST_CHRONO)
endif()
qi_persistent_set(BOOST_THREAD_DEPENDS ${_deps})
