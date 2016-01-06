## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(GTEST)
fpath(GTEST gtest/gtest.h)

if (MSVC)
  flib(GTEST OPTIMIZED gtest)
  flib(GTEST OPTIMIZED gtest_main-md)
  flib(GTEST DEBUG     gtestd)
  flib(GTEST DEBUG     gtest_main-mdd)
else()
  flib(GTEST gtest)
  flib(GTEST gtest_main)
endif()

qi_persistent_set(GTEST_DEPENDS "PTHREAD")
export_lib(GTEST)
