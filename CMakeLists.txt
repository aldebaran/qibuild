##
## Author(s):
##  - Cedric GESTES      <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

cmake_minimum_required(VERSION 2.6.4)

project(qiBuild NONE)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/")

message("CMAKE_MODULE_PATH=${CMAKE_MODULE_PATH}")

include("qibuild/qibuild")

add_subdirectory("cmake/samples")
