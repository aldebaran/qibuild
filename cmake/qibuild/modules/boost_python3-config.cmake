## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/boostutils.cmake")

# boost-python3 have different names depending on the distribution,
# it's libboost_python3.so on archlinux but libboost_python-py33.so on ubuntu
boost_flib(PYTHON3 "python3" "python-py34" "python-py33" "python-py32" "python-py31")
qi_persistent_set(BOOST_PYTHON3_DEPENDS "PYTHON3")
