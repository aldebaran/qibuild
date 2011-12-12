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

#! Logging messages
# =================
#
# This modules implements log messages with different verbosity levels.
# By default debug and verbose are disabled.
# If you want the verbose output call cmake with a VERBOSE=1 environment variable set.
# If you want the debug output call cmake with a DEBUG=1 environment variable set.
# You can combine DEBUG and VERBOSE.
#
# You can also trigger deprectated warning messages with QI_WARN_DEPRECATED (OFF
# by default)

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

