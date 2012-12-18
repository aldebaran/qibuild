## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
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
list(APPEND _deps BOOST_CHRONO)
qi_set_global(BOOST_THREAD_DEPENDS ${_deps})
