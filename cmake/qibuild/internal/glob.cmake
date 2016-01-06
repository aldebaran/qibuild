## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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
