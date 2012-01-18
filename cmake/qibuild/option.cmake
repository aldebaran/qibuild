## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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
#   # Add some foo-dependent sources when buidling bar library:
#   set(bar_srcs
#         bar_spam.cpp
#         bar_eggs.cpp
#   )
#   if(WITH_FOO)
#      list(APPEND bar_srcs bar_foo.cpp)
#   endif()
#
#   qi_create_bin(bar ${bar_srcs})
#   qi_use_lib(bar SPAM EGGS)
#   if(WITH_FOO)
#      qi_use_lib(bar FOO)
#   endif()
#
# .. note:: if the foo package is found, WITH_FOO will automatically be set to true.
#       however, there are a few cases where you would like to NOT use the
#       features of the FOO library even if it is found, in this case, we let
#       the user set -DWITH_FOO=OFF from the command line.
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

