##
# Copyright (C) 2010 Aldebaran Robotics
#

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

qi_create_lib(bar
  bar/bar.h
  bar/bar.cpp)

qi_stage_lib(bar)
qi_install_header(bar bar/bar.h)

