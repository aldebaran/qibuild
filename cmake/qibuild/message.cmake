##
## debug.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Sat Oct 10 02:45:29 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

############################
#
# display debug
#
############################
function(debug)
  if($ENV{DEBUG})
    message(STATUS "${ARGN}")
  endif($ENV{DEBUG})
endfunction(debug)

############################
#
# display verbose
#
############################
function(verbose)
  if($ENV{VERBOSE})
    message(STATUS "${ARGN}")
  endif($ENV{VERBOSE})
endfunction(verbose)

############################
#
# display info
#
############################
function(info)
  if(DEFINED ENV{INFO})
    if($ENV{INFO} EQUAL 0)
      return()
    endif($ENV{INFO} EQUAL 0)
  endif(DEFINED ENV{INFO})

  message(STATUS "${ARGN}")
endfunction(info)

############################
#
# display warning
#
############################
function(warning)
  message(WARNING "${ARGN}")
endfunction(warning)

############################
#
# display error
#
############################
function(error)
  message(STATUS "${ARGN}")
  #use "" to force the use of ; when displaying list
  message(FATAL_ERROR "")
endfunction(error)

