## Copyright (C) 2011 Aldebaran Robotics

#export share/cmake, include, lib
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
list(APPEND CMAKE_PREFIX_PATH "${_ROOT_DIR}")
