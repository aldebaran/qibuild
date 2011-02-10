## Copyright (C) 2011 Aldebaran Robotics

include(CMakeParseArguments)

#!
# include a subdirectory if all options are ON
# \arg:subdir the subdirectory that should be added to the build
# \argn: condi
function(qi_add_subdirectory subdir)
  cmake_parse_arguments(ARG "" "" "IF" ${ARGN})
  set(ARG_IF ${ARG_IF} ${ARG_UNPARSED_ARGUMENTS})
  set(_do_the_include 1)
  foreach(_arg ${ARG_IF})
    if (${_arg})
    else()
      set(_do_the_include 0)
      break()
    endif()
  endforeach()
  if (${_do_the_include})
    add_subdirectory(${subdir})
  endif()
endfunction()
