## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8)
# find_package should be after project
# because the toolchain file is read only
# after project() has been called
find_package(qibuild)
project(incorrect)
