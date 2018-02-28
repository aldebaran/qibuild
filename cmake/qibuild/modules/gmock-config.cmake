## Copyright (c) 2012-2018 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Find gmock
clean(GMOCK)
fpath(GMOCK gmock/gmock.h)

if (MSVC)
  flib(GMOCK OPTIMIZED gmock)
  flib(GMOCK DEBUG gmockd)
else()
  flib(GMOCK gmock)
endif()

qi_persistent_set(GMOCK_DEPENDS "GTEST")
export_lib(GMOCK)

# Find gmock_main
clean(GMOCK_MAIN)
fpath(GMOCK_MAIN gmock/gmock.h)

if (MSVC)
  flib(GMOCK_MAIN OPTIMIZED gmock_main-md)
  flib(GMOCK_MAIN DEBUG gmock_main-mdd)
else()
  flib(GMOCK_MAIN gmock_main)
endif()

qi_persistent_set(GMOCK_MAIN_DEPENDS "GMOCK")
export_lib(GMOCK_MAIN)
