## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

boost_flib("locale")
qi_persistent_set(BOOST_LOCALE_DEPENDS "BOOST_THREAD")
if (APPLE)
  qi_persistent_set(BOOST_LOCALE_DEPENDS "BOOST_THREAD" "ICONV")
endif()
