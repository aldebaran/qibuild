## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Logging messages
# =================
#
# This modules implements log messages with different verbosity levels.
# By default debug and verbose are disabled.
# If you want the verbose output call cmake with a VERBOSE=1 environment variable set.
# If you want the debug output call cmake with a DEBUG=1 environment variable set.
# You can combine DEBUG and VERBOSE.
#
# You can also trigger deprecated warning messages with QI_WARN_DEPRECATED (OFF
# by default)

#! display a debug message
# To enable debug output set DEBUG=1 in your environment.
# \argn: a message
function(qi_debug)
  if($ENV{DEBUG})
    message(STATUS "${ARGN}")
  endif()
endfunction()

#! display a verbose message
# To enable verbose output set VERBOSE=1 in your environment.
# \argn: a message
function(qi_verbose)
  if($ENV{VERBOSE})
    message(STATUS "${ARGN}")
  endif()
endfunction()

#! display an info message
# \argn: a message
function(qi_info)
  if(DEFINED ENV{INFO})
    if($ENV{INFO} EQUAL 0)
      return()
    endif()
  endif()

  message(STATUS "${ARGN}")
endfunction()

#! display a deprecated message
# \argn: a message
function(qi_deprecated)
  set(_warn OFF)
  if(QI_WARN_DEPRECATED)
    set(_warn ON)
  endif()

  if(_warn)
    message(WARNING "DEPRECATED: ${ARGN}")
  endif()
endfunction()

#! display a warning message
# \argn: a message
function(qi_warning)
  message(WARNING "${ARGN}")
endfunction()

#! display an error message
# \argn: a message
function(qi_error)
  message(STATUS "${ARGN}")
  #use "" to force the use of ; when displaying list
  message(FATAL_ERROR "")
endfunction()

