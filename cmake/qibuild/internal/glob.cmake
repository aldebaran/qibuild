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

function(qi_glob _OUT_srcs)
  set(_temp)
  foreach(_arg ${ARGN})
    #is this a globbing expression?
    if ("${_arg}" MATCHES "(\\*)|(\\[.*\\])")
      file(GLOB _glob "${_arg}")
      if ("${_glob}" STREQUAL "")
        qi_error("${_arg} does not match")
      else()
        set(_temp ${_temp} ${_glob})
      endif()
    else()
      set(_temp ${_temp} ${_arg})
    endif()
  endforeach()
  set(${_OUT_srcs} ${_temp} PARENT_SCOPE)
endfunction()

function(qi_abspath _OUT_srcs)
  set(_temp)
  foreach(_arg ${ARGN})
    get_filename_component(_abspath ${_arg} ABSOLUTE)
    list(APPEND _temp "${_abspath}")
  endforeach()
  set(${_OUT_srcs} ${_temp} PARENT_SCOPE)
endfunction()
