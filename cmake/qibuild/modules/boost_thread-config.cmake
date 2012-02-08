## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

clean(BOOST_THREAD)
fpath(BOOST_THREAD boost/config.hpp)
boost_flib(THREAD "thread")
qi_set_global(BOOST_THREAD_DEPENDS "BOOST_DATE_TIME;PTHREAD")
export_lib(BOOST_THREAD)
