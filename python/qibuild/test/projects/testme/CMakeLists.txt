## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
cmake_minimum_required(VERSION 2.8)
project(runtests)

find_package(qibuild)
qi_create_test(ok ok.cpp)
qi_create_test(fail fail.cpp)
qi_create_test(cwd
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  ARGUMENTS ${CMAKE_SOURCE_DIR}
  SRC cwd.cpp)
qi_create_test(segfault segfault.cpp)
qi_create_test(timeout timeout.cpp TIMEOUT 1)
qi_create_test(spam spam.cpp)
qi_create_test(encoding encoding.cpp)
qi_create_test(fake_gtest fake_gtest.cpp ARGUMENTS "${QI_SDK_DIR}/test-results/fake_gtest.xml")
qi_create_test(nightly nightly.cpp NIGHTLY)
qi_create_test(env env.cpp ENVIRONMENT
  "FOO=BAR;SPAM=EGGS")
qi_create_test(fdleak fdleak.cpp)
qi_create_perf_test(perf perf.cpp PERF)
