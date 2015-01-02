## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
project(debugme)

find_package(qibuild)

# Create a executable named debugme
# with the source file: main.cpp
qi_create_bin(debugme "main.cpp")
