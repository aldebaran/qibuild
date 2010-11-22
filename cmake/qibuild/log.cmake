##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

############################
#
# display debug
#
############################
function(qi_debug)
  if($ENV{DEBUG})
    message(STATUS "${ARGN}")
  endif($ENV{DEBUG})
endfunction()

############################
#
# display verbose
#
############################
function(qi_verbose)
  if($ENV{VERBOSE})
    message(STATUS "${ARGN}")
  endif($ENV{VERBOSE})
endfunction()

############################
#
# display info
#
############################
function(qi_info)
  if(DEFINED ENV{INFO})
    if($ENV{INFO} EQUAL 0)
      return()
    endif($ENV{INFO} EQUAL 0)
  endif(DEFINED ENV{INFO})

  message(STATUS "${ARGN}")
endfunction()

############################
#
# display warning
#
############################
function(qi_warning)
  message(WARNING "${ARGN}")
endfunction()

############################
#
# display error
#
############################
function(qi_error)
  message(STATUS "${ARGN}")
  #use "" to force the use of ; when displaying list
  message(FATAL_ERROR "")
endfunction()

