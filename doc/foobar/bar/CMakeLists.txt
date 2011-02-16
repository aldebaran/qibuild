##
# Copyright (C) 2010 Aldebaran Robotics
#

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_library(bar
  bar/bar.h
  bar/bar.cpp)

install(TARGETS bar
  RUNTIME DESTINATION "lib"
  ARCHIVE DESTINATION "lib"
  LIBRARY DESTINATION "lib")


install(FILES bar/bar.h
  DESTINATION "include/bar")
