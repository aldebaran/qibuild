cmake_minimum_required(VERSION 2.8)
project(@project_name@)

## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
find_package(qibuild)

# Create a executable named @project_name@
# with the source file: main.cpp
qi_create_bin(@project_name@ "main.cpp")

# Add a simple test:
enable_testing()
qi_create_test(test_@project_name@ "test.cpp")

