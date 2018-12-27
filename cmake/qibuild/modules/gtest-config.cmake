## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Find gtest
clean(GTEST)
fpath(GTEST gtest/gtest.h)
flib(GTEST gtest)

qi_persistent_set(GTEST_DEPENDS "PTHREAD")
export_lib(GTEST)

# Find gtest_main
clean(GTEST_MAIN)
fpath(GTEST_MAIN gtest/gtest.h)
flib(GTEST_MAIN gtest_main)

qi_persistent_set(GTEST_MAIN_DEPENDS "GTEST")
export_lib(GTEST_MAIN)
