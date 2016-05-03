## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(foo C)

find_package(qibuild)

include_directories(".")
qi_create_lib(foo "foo.c")
qi_use_lib(foo BAR)
qi_stage_lib(foo)
qi_install_header(foo.h)
