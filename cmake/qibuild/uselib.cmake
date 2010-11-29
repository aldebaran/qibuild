##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

if (_QI_USELIB_CMAKE_)
  return()
endif()
set(_QI_USELIB_CMAKE_ TRUE)


#!
# Find dependencies and add them to the target <name>.
#
# \arg:name the target to add dependencies to
# \flag:OPTIONAL do not stop on error
# \group:DEPENDENCIES the list of dependencies
function(qi_use_lib name)
  cmake_parse_arguments(ARG "OPTIONAL" "PLATEFORM" "DEPENDENCIES" ${ARGN})

  set(ARG_DEPENDENCIES ${ARGN} ${ARG_DEPENDENCIES})

  foreach(_pkg ${ARG_DEPENDENCIES})
    find_package(${_pkg})
    include_directories(${${_pkg}_INCLUDE_DIR})
    target_link_libraries("${name}" ${${_pkg}_LIBRARIES})
    #TODO: add_dependencies

    #TODO: target properties
    set_directory_properties(PROPERTIES COMPILE_DEFINITIONS "${${_pkg}_DEFINITIONS}")
  endforeach()

endfunction()
