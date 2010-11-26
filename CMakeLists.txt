##
## Author(s):
##  - Cedric GESTES      <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

cmake_minimum_required(VERSION 2.6.4)

project(QiBuild NONE)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/")

message("CMAKE_MODULE_PATH=${CMAKE_MODULE_PATH}")

include("qibuild/qibuild")

#include("qibuild/expect_test")
#include("qibuild/submodule_test")

add_subdirectory("cmake/samples")
