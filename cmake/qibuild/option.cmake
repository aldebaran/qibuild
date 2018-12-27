## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
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

  if(DEFINED "WITH_${_U_name}")
    # this can happen if the flag has been set by user, or
    # if we are coming from  `cmake ..`
    if(WITH_${_U_name})
      # re-find the package, in case the
      # -config contains some macros:
      find_package("${_U_name}" QUIET)
    else()
      # user forced WITH_* to OFF:
      return()
    endif()
  else()
    # call option() with the correct default value.
    # note that this will automatically set the WITH_* variable
    # in the cache
    find_package("${_U_name}" QUIET)
    if(${_U_name}_PACKAGE_FOUND)
      option("WITH_${_U_name}" "${_desc}" ON)
    else()
      option("WITH_${_U_name}" "${_desc}" OFF)
    endif()
    # re-set PACKAGE_FOUND to not break qi_use_lib
    qi_persistent_set(${_U_name}_PACKAGE_FOUND FALSE)
  endif()
endfunction()

