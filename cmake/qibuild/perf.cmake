## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


#! Function to generate perf stats

include(CMakeParseArguments)

#!
# Create a perf test
# It is assumed that the executable will understand an option
# named "--output <out.xml>" and generate such a file.
# You can for instance use the qiperf library for that.
#
# Notes:
#  * The test won't be built if BUILD_PERFS_TESTS is OFF
#
# \arg:name Name of the test. A target of this name will be created
# \group:SRC Sources of the perf executable
# \group:DEPENDS Dependencies to pass to qi_use_lib
# \group:ARGUMENTS arguments to be passed to the executable
#
function(qi_create_perf_test name)
  if (DEFINED BUILD_PERFS_TESTS AND NOT BUILD_PERFS_TESTS)
    qi_debug("Perf test(${name}) disabled by BUILD_PERFS_TESTS=OFF")
    qi_set_global(QI_${name}_TARGET_DISABLED TRUE)
    return()
  endif()
  cmake_parse_arguments(ARG "" "" "SRC;DEPENDS;ARGUMENTS" ${ARGN})
  set(_src ${ARG_UNPARSED_ARGUMENTS} ${ARG_SRC})
  set(_deps ${ARG_DEPENDS})
  set(_args ${ARG_ARGUMENTS})

  # create the executable:
  qi_create_bin(${name} ${_src} NO_INSTALL DEPENDS ${_deps})

  set(_perf_dir ${CMAKE_BINARY_DIR}/perf-results)
  file(MAKE_DIRECTORY ${_perf_dir})

  set(_out_file ${_perf_dir}/${name}.xml)
  # add it to the list, to be run with qibuild test --perf
  set(_to_write "${name}")
  if (NOT "${_args}" STREQUAL "")
    set(_to_write "${_to_write};${_args}")
  endif()
  set(_to_write "${_to_write}\n")
  file(APPEND ${CMAKE_BINARY_DIR}/perflist.txt "${_to_write}")

endfunction()
