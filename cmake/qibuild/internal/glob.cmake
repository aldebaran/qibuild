##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

function(qi_glob_sources _OUT_srcs)
  set(_temp)
  foreach(_arg ${ARGN})
    file(GLOB _glob "${_arg}")
    set(_temp ${_temp} ${_glob})
    #message("TEMP: ${_temp}")
  endforeach()

  #message("TEMPEND: ${_temp}")

  set(${_OUT_srcs} ${_temp} PARENT_SCOPE)
endfunction()


function(qi_glob_sources2 _OUT_srcs)
  set(_temp)
  foreach(_arg ${ARGN})
    if(IS_ABSOLUTE _arg)
      set(_src ${_arg})
    else()
      set(_src "${CMAKE_CURRENT_SOURCE_DIR}/${_arg}")
    endif()
    if(IS_DIRECTORY ${_src})
      message(STATUS "DIR: ${_src}")
      file(GLOB _glob RELATIVE "${_src}" "*.hpp" "*.h" "*.hxx")
      set(_temp ${_temp} ${_glob})

      # file(GLOB _glob RELATIVE "${_src}" "*.h")
      # set(_temp ${_temp} ${_glob})

      # file(GLOB _glob RELATIVE "${_src}" "*.hxx")
      # set(_temp ${_temp} ${_glob})

      # file(GLOB _glob "${_src}" "*.c")
      # set(_temp ${_temp} ${_glob})

      # file(GLOB _glob "${_src}" "*.cc")
      # set(_temp ${_temp} ${_glob})

      # file(GLOB _glob "${_src}" "*.cpp")
      # set(_temp ${_temp} ${_glob})
    else()
      if(EXISTS ${_src})
        message(STATUS "FILE: ${_src}")
        set(_temp ${_temp} ${_src})
      endif()
    endif()
    message("TEMP: ${_temp}")
  endforeach()

  message("TEMPEND: ${_temp}")

  set(${_OUT_srcs} ${_temp} PARENT_SCOPE)
endfunction()
