##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

#! QiBuild Log
# ============
# Cedric GESTES <gestes@aldebaran-robotics.com>

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
  endif($ENV{DEBUG})
endfunction()

#! display a vebose message
# To enable verbose output set VERBOSE=1 in your environment.
# \argn: a message
function(qi_verbose)
  if($ENV{VERBOSE})
    message(STATUS "${ARGN}")
  endif($ENV{VERBOSE})
endfunction()

#! display an info message
# \argn: a message
function(qi_info)
  if(DEFINED ENV{INFO})
    if($ENV{INFO} EQUAL 0)
      return()
    endif($ENV{INFO} EQUAL 0)
  endif(DEFINED ENV{INFO})

  message(STATUS "${ARGN}")
endfunction()

#! display a deprecated message
# \argn: a message
function(qi_deprecated)
  message(WARNING "DEPRECATED: ${ARGN}")
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

