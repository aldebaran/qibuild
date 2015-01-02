## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

if (Boost_VERSION GREATER 105300 OR Boost_VERSION EQUAL 105300)
boost_flib("lockfree")
qi_persistent_set(BOOST_LOCKFREE_DEPENDS BOOST_ATOMIC)
endif()
