## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

set(_libname "signals")
set(_suffix "SIGNALS")

clean(BOOST_${_suffix})
fpath(BOOST_${_suffix} boost/config.hpp)
boost_flib(${_suffix} ${_libname})
export_lib(BOOST_${_suffix})
