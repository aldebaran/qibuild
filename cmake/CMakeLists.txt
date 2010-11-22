##
## CMakeLists.txt
## Login : <ctaf@ctaf-maptop>
## Started on  Sat Sep 12 03:01:43 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##


cmake_minimum_required(VERSION 2.6.4)
project("t001chain")
include("bootstrap.cmake")

file(GLOB _cmakes RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}/" "*.cmake")
install_cmake("" ${_cmakes})

add_subdirectory("templates")
add_subdirectory("modules")

add_subdirectory("package")
