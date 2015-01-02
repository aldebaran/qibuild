## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Required so that FindBoost.cmake does not try to include this file
set(Boost_NO_BOOST_CMAKE TRUE)
find_package(Boost QUIET)
qi_persistent_set(BOOST_INCLUDE_DIRS ${Boost_INCLUDE_DIRS})
export_header(BOOST)
