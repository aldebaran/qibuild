## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(cov)

find_package(qibuild)
qi_sanitize_compile_flags()
# Create a executable named cov
# with the source file: main.cpp
qi_create_bin(cov "main.cpp")

# Add a simple test:
qi_create_test(test_cov "test.cpp")
