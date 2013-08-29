## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
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

#! Create a new test that can be run by CTest or `qibuild test`
#
# Notes:
#  * The resulting executable will not be installed
#  * The name of the test will always be the name of the target.
#  * The test won't be built if BUILD_TESTS is OFF
#
# .. seealso::
#
#    * :ref:`qibuild-ctest`
#
# \arg:name the name of the test and the target
# \group:SRC  sources of the test
# \group:DEPENDS the dependencies of the test
# \param:TIMEOUT the timeout of the test.
# \flag: NIGHTLY: only compiled (and thus run) if QI_NIGHTLY_TESTS is ON
# \group:ARGUMENTS arguments to be passed to the executable
# \argn: source files (will be merged with the SRC group of arguments)
function(qi_create_test name)
  qi_add_test(${name} ${name} ${ARGN})
endfunction()


#! This compiles and add a test using gtest that can be run by CTest or
# `qibuild test`
#
# When running ctest, an XML xUnit file wiil be created in
# ${CMAKE_SOURCE_DIR}/test-results/${test_name}.xml
#
# Notes:
#
#  * The test won't be built at all if GTest is not found.
#  * The name of the test will always be the name of the target.
#
# .. seealso::
#
#    * :ref:`qibuild-ctest`
#
# \arg:name name of the test
# \flag:NO_ADD_TEST Do not call add_test, just create the binary
# \flag: NIGHTLY: only compiled (and thus run) if QI_NIGHTLY_TESTS is ON
# \argn: source files, like the SRC group, argn and SRC will be merged
# \param:TIMEOUT The timeout of the test
# \group:SRC Sources
# \group:DEPENDS Dependencies to pass to qi_use_lib
# \group:ARGUMENTS Arguments to pass to add_test (to your test program)
#
function(qi_create_gtest name)
  qi_add_test(${name} ${name} GTEST ${ARGN})
endfunction()

#!
# Create a perf test
# It is assumed that the executable will understand an option
# named "--output <out.xml>" and generate such a file.
# You can for instance use the qiperf library for that.
#
# Notes:
#  * The test won't be built if BUILD_PERF_TESTS is OFF
#
# \arg:name Name of the test. A target of this name will be created
# \group:SRC Sources of the perf executable
# \group:DEPENDS Dependencies to pass to qi_use_lib
# \group:ARGUMENTS arguments to be passed to the executable
#
function(qi_create_perf_test name)
  _qi_add_test(${name} ${name} PERF ${ARGN})
endfunction()


#! Add a test using an existing binary
#
# * We look for the binary in sdk/bin, as a target, or an external
#   package, and we know there is a``_d `` when using Visual Studio on debug
# * We set a ``tests`` folder property
#
# This is a low-level function, you should rather use
# :cmake:function:`qi_create_test` or :cmake:function:`qi_create_gtest` instead.
#
# \arg:test_name The name of the test
# \arg:target_name The name of the binary to use. It can be a target name,
#                  an absolute or relative path to an existing file,
#                  or a package name providing a ${name}_EXECUTABLE variable.
# \flag: NIGHTLY: only compiled (and thus run) if QI_NIGHTLY_TESTS is ON
# \group:ARGUMENTS Arguments to be passed to the executable
function(qi_add_test test_name target_name)
  _qi_add_test(${test_name} ${target_name} ${ARGN})
endfunction()
