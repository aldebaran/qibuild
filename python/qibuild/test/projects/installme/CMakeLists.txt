## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(installme)

find_package(qibuild)
include(qibuild/swig/python)

qi_install_data(data/* SUBFOLDER data_star)

# relative paths
qi_install_header(relative/foo/foo.h relative/bar/bar.h
  KEEP_RELATIVE_PATHS)

# recurse
qi_install_data(recurse/*
  RECURSE KEEP_RELATIVE_PATHS)

if (FAIL_EMPTY_GLOB)
  qi_install_data(nonexisting/*)
endif()

qi_install_data(data/bar.dat SUBFOLDER sub)

if (FAIL_NON_EXISTING)
  qi_install_data(nonexisting)
endif()

qi_install_python("py")
qi_install_python("py" SUBFOLDER sub)

# test
qi_create_test_lib(foo foo.cpp)
qi_swig_wrap_python(foo foo.i foo.cpp SUBFOLDER sub_swig)
qi_install_test_data(test_data.dat)
