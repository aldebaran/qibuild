## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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

