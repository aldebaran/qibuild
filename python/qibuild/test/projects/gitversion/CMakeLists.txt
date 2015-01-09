## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(gitversion)

find_package(qibuild)

qi_get_git_version(git_version)

qi_create_bin(testversion "main.cpp")

set_source_files_properties("main.cpp"
  PROPERTIES
    COMPILE_DEFINITIONS "VERSION=\"${git_version}\"")
