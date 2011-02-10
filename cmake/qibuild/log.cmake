## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild Log
# ============

#!
# This modules implement log message with different verbose level.
# By default debug and verbose are disable.
# If you want the verbose output call cmake with a VERBOSE=1 environment variable set.
# If you want the debug output call cmake with a DEBUG=1 environment variable set.
# You can combine DEBUG and VERBOSE.
#

#! display a debug message
# To enable debug output set DEBUG=1 in your environment.
# \argn: a message
function(qi_debug)
  if($ENV{DEBUG})
    message(STATUS "${ARGN}")
  endif()
endfunction()

#! display a vebose message
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
  if(NO_WARN_DEPRECATED)
    return()
  else()
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

