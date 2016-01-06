## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(ODE)
fpath(ODE ode/ode.h)
if(UNIX)
  # Check whether we should define -DdDOUBLE
  find_program(_ode_config ode-config QUIET)
  if(_ode_config)
    # execute ode-config --cflags
    execute_process(COMMAND ${_ode_config} "--cflags"
      OUTPUT_VARIABLE _output
    )
    string(REGEX MATCH "-DdSINGLE" _single ${_output})
    if(_single)
      add_definitions("-DdSINGLE")
    endif()
    string(REGEX MATCH "-DdDOUBLE" _double ${_output})
    if(_double)
      add_definitions("-DdDOUBLE")
    endif()
  endif()
endif()
flib(ODE ode)
export_lib(ODE)
