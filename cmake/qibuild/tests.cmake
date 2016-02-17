## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Testing
# ========
#
# This CMake module provides functions to interface gtest with ctest.
#
# .. seealso::
#
#    * :ref:`qibuild-ctest`
#

include(qibuild/internal/tests)

#! Create a new test that can be run by ``qitest run``
#
# Notes:
#  * The test can be installed using ``qibuild install --with-tests``
#  * The name of the test will always be the name of the target.
#  * The test won't be configured or built if QI_WITH_TESTS is OFF
#
# \arg:name the name of the test and the target
# \group:SRC  sources of the test
# \group:DEPENDS the dependencies of the test
# \param:TIMEOUT the timeout of the test, in seconds. Defaults to 20
# \param:WORKING_DIRECTORY working directory used when running the test:
#                          default: ``<build>/sdk>/bin``
# \flag: NIGHTLY: only compiled (and thus run) if QI_WITH_NIGHTLY_TESTS is ON
# \flag: PERF: only compiled (and thus run) if QI_WITH_PERF_TESTS is ON
#              It is assumed that the executable will understand an option
#              named "--output <out.xml>" and generate such a file.
#              You can for instance use the qiperf library for that.
# \group:ARGUMENTS arguments to be passed to the executable
# \group:ENVIRONMENT list of environment variables for the tests, in the form
#                    "key1=value1;key2=value2"
# \argn: source files (will be merged with the SRC group of arguments)
function(qi_create_test name)
  qi_add_test(${name} ${name} ${ARGN})
endfunction()


#! Add a test helper
# Create a binary that will not be run as a test, but rather used
# by an other test.
#
# The helper can be installed along the proper tests using
# ``qibuild install --with-tests``
#
# Arguments are the same as :cmake:function:`qi_create_bin`
function(qi_create_test_helper name)
  if(NOT QI_WITH_TESTS)
    return()
  endif()

  qi_create_bin(${name} NO_INSTALL ${ARGN})
  if(TARGET ${name})
    install(TARGETS ${name}
            DESTINATION "bin"
            COMPONENT "test")
    set_target_properties(${name} PROPERTIES FOLDER tests)
  endif()
endfunction()

#! Add a test library.
#
# The library can be installed along the other tests binaries using
# ``qibuild install --with-tests``
#
# Arguments are the same as :cmake:function:`qi_create_lib`
function(qi_create_test_lib target_name)
  qi_create_lib(${target_name} ${ARGN} NO_INSTALL)

  if(WIN32)
    set(_runtime_output ${QI_SDK_BIN})
  else()
    set(_runtime_output ${QI_SDK_LIB})
  endif()

  # Never install static tests libs
  get_target_property(_type ${target_name} TYPE)
  if("${_type}" STREQUAL "STATIC_LIBRARY")
    return()
  endif()
  install(TARGETS ${target_name}
    RUNTIME COMPONENT test DESTINATION ${_runtime_output}
    LIBRARY COMPONENT test DESTINATION ${_runtime_output}
  )

endfunction()

#! Add a test using an existing binary. Arguments are the same as
#  :cmake:function:`qi_create_test`
#
# The ``target_name`` should match either:
#   * a target
#   * a binary found by ``find_program(${target_name})``
#   * the name of a package defining ``${${target_name}_EXECUTABLE}}``
#
# This can be used for instance to create several tests with one target::
#
#      qi_create_test_helper(test_foo test_foo.cpp)
#      qi_add_test(test_foo_one test_foo ARGUMENTS --one)
#      qi_add_test(test_foo_two test_foo ARGUMENTS --two)
#
function(qi_add_test test_name target_name)
  _qi_add_test_internal(${test_name} ${target_name} ${ARGN})
endfunction()

#! Same as :cmake:function:`qi_create_test`, excepts it adds a dependency
# to the gtest libraries
function(qi_create_gtest name)
  qi_add_test(${name} ${name} GTEST_TEST ${ARGN})
endfunction()

#! Same as :cmake:function:`qi_create_test`, excepts it adds a dependency
# to the ``gmock`` libraries
function(qi_create_gmock name)
  qi_add_test(${name} ${name} GMOCK_TEST ${ARGN})
endfunction()

#! Shortcut for :cmake:function:`qi_create_test(... PERF) <qi_create_test>`
function(qi_create_perf_test name)
  _qi_add_test_internal(${name} ${name} PERF_TEST ${ARGN})
endfunction()
