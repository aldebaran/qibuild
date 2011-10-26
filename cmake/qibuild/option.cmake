## Copyright (C) 2011 Aldebaran Robotics

#!
# Using options
# =============

#! Add optional dependency to a package
#
# Example::
#
#   # Create a WITH_FOO option if FOO_PACKAGE is found
#   qi_add_optional_package(FOO)
#
#   if(WITH_FOO)
#      ...
#   endif()
#
# \arg:  NAME             Name of the package, a WITH_${NAME} option will be created
# \arg:  DESCRIPTION      The description of the option (will be shown in cmake gui)
#
function(qi_add_optional_package name)
  set(_desc "${ARGN}")
  string(TOUPPER "${name}" _U_name)

  # if already set by user, do nothing:
  if(DEFINED "WITH_${_U_name}")
    return()
  endif()

  option("WITH_${_U_name}" "${_desc}" OFF)

  # else, set the value of the option using the
  # result of find_package

  find_package("${_U_name}" QUIET)

  if(${_U_name}_PACKAGE_FOUND)
    set("WITH_${_U_name}" ON CACHE BOOL "${_desc}" FORCE)
  else()
    set("WITH_${_U_name}" OFF CACHE BOOL "${_desc}" FORCE)
  endif()
endfunction()

