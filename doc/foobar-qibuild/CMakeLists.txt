##
# Copyright (C) 2010 Aldebaran Robotics
#

cmake_minimum_required(VERSION 2.8)

project(foobar)

include(qibuild.cmake)

add_subdirectory(bar)

add_subdirectory(foo)
