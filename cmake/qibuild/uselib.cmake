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
    string(TOUPPER ${_pkg} _U_PKG)
    #TODO: search for INCLUDE_DIRS, fallback on INCLUDE_DIR
    if (DEFINED ${_U_PKG}_INCLUDE_DIRS)
      include_directories(${${_U_PKG}_INCLUDE_DIRS})
    elseif(DEFINED ${_U_PKG}_INCLUDE_DIR)
      include_directories(${${_U_PKG}_INCLUDE_DIR})
    endif()

    if (DEFINED ${_U_PKG}_DEPENDS)
      message(STATUS "loop: ${${_U_PKG}_DEPENDS}")
      qi_use_lib(${name} ${${_U_PKG}_DEPENDS})
    endif()

    message(STATUS "lib: ${${_U_PKG}_LIBRARIES}")
    target_link_libraries("${name}" ${${_U_PKG}_LIBRARIES})
    #TODO: add_dependencies
    #TODO: target properties
    set_directory_properties(PROPERTIES COMPILE_DEFINITIONS "${${_U_PKG}_DEFINITIONS}")
  endforeach()
  string(TOUPPER "${name}" _U_name)
  qi_set_global("${_U_name}_DEPENDS" ${${_U_name}_DEPENDS} ${ARG_DEPENDENCIES})
  message("${_U_name}_DEPENDS = ${ARG_DEPENDENCIES}")
endfunction()
