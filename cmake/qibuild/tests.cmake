## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Testing
# ========
#
# This CMake module provides functions to interface gtest with ctest.
#


set(_TESTS_RESULTS_FOLDER "${CMAKE_SOURCE_DIR}/build-tests/results" CACHE INTERNAL "" FORCE)



#! Create a new test.
# Note that the resulting executable will NOT
# be installed by default.
# The name of the test will match the target name
#
# \arg:name the name of the test and the target
# \group:SRC  sources of the test
# \group:DEPENDS the dependencies of the test
# \param:TIMEOUT the timeout of the test
# \group:ARGUMENTS arguments to be passed to the executable
# \flag:INSTALL wether the test should be installed (false by default)
# \argn: source files (will be merged with the SRC group of arguments)
#
function(qi_create_test name)
  cmake_parse_arguments(ARG "INSTALL" "TIMEOUT" "SRC;DEPENDS;ARGUMENTS" ${ARGN})
  qi_create_bin(${name} SRC ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS} NO_INSTALL)
  if(ARG_DEPENDS)
    qi_use_lib(${name} ${ARG_DEPENDS})
  endif()
  qi_add_test(${name} ${name}
    TIMEOUT ${ARG_TIMEOUT}
    ARGUMENTS ${ARG_ARGUMENTS}
  )
endfunction()


#! This compiles and add_test's a CTest test that uses gtest.
# (so that the test can be run by CTest)
#
# When running ctest, an XML xUnit xml file wiil be created to
# ${CMAKE_SOURCE_DIR}/test-results/${test_name}.xml
#
# The name of the test will always be the name of the target.
#
# \arg:name name of the test
# \flag:NO_ADD_TEST Do not call add_test, just create the binary
# \argn: source files, like the SRC group, argn and SRC will be merged
# \param:TIMEOUT The timeout of the test
# \group:SRC Sources
# \group:DEPENDS Dependencies to pass to use_lib
# \group:ARGUMENTS Arguments to pass to add_test (to your test program)
function(qi_create_gtest name)
  if(NOT DEFINED GTEST_PACKAGE_FOUND)
    find_package(GTEST NO_MODULE)
    if(NOT GTEST_PACKAGE_FOUND)
      qi_set_global(GTEST_PACKAGE_FOUND FALSE)
    endif()
  endif()

  if(NOT GTEST_PACKAGE_FOUND)
    if(NOT QI_CREATE_GTEST_WARNED)
      qi_info("GTest was not found:
      qi_create_gtest will create no target
      ")
      qi_set_global(QI_CREATE_GTEST_WARNED TRUE)
    endif()
    qi_set_global(QI_${name}_TARGET_DISABLED TRUE)
    return()
  endif()

  set(_using_qibuild_gtest TRUE)
  # Make sure we are using the qibuild flavored gtest
  # package:
  find_package(gtest_main QUIET)
  if(NOT GTEST_MAIN_PACKAGE_FOUND)
    set(_using_qibuild_gtest FALSE)
    if(NOT QI_GTEST_QIBUID_WARNED)
      qi_info("Could not find qibuild flavored gtest. (not GTEST_MAIN package)
      Please use a qibuild port of gtest or be ready to
      experience weird link errors ...
      ")
      qi_set_global(QI_GTEST_QIBUID_WARNED TRUE)
    endif()
  endif()

  if (DEFINED BUILD_TESTS AND NOT BUILD_TESTS)
    qi_debug("Test(${name}) disabled by BUILD_TESTS=OFF")
    return()
  endif()
  # create tests_results folder if it does not exist
  file(MAKE_DIRECTORY "${_TESTS_RESULTS_FOLDER}")
  cmake_parse_arguments(ARG "NO_ADD_TEST" "TIMEOUT" "SRC;DEPENDS;ARGUMENTS" ${ARGN})

  # First, create the target
  qi_create_bin(${name} SRC ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS} NO_INSTALL)
  qi_use_lib(${name} GTEST ${ARG_DEPENDS})
  if(${_using_qibuild_gtest})
    qi_use_lib(${name} GTEST_MAIN)
  endif()

  # Build a correct xml output name
  set(_xml_output "${_TESTS_RESULTS_FOLDER}/${name}.xml")

  if (WIN32)
    string(REPLACE "/" "\\\\" xml_output ${_xml_output})
  endif()


  # Call qi_add_test with correct arguments:
  # first, --gtest_output:
  set(_args --gtest_output=xml:${_xml_output})

  # then, arguments coming from the user:
  list(APPEND _args  ${ARG_ARGUMENTS})

  qi_add_test(${name} ${name}
    TIMEOUT ${ARG_TIMEOUT}
    ARGUMENTS ${_args}
  )
endfunction()

#! Add a test using a binary that was created by qi_create_bin
# This calls add_test() with the same arguements but:
#
#  * We look for the binary in sdk/bin, and we know
#    there is a _d when using Visual Studio
#  * We set a 'tests' folder property
#  * We make sure necessary environment variables are set on mac
#
# This is a low-level function, you should rather use
# :cmake:function:`qi_create_test` or :cmake:function:`qi_create_gtest` instead.
#
# \arg:test_name The name of the test
# \arg:target_name The name of the binary to use
# \param:TIMEOUT The timeout of the test
# \group:ARGUMENTS Arguments to be passed to the executable
function(qi_add_test test_name target_name)
  cmake_parse_arguments(ARG "" "TIMEOUT" "ARGUMENTS" ${ARGN})

  if(NOT ARG_TIMEOUT)
    set(ARG_TIMEOUT 20)
  endif()

  set(_bin_path ${QI_SDK_DIR}/${QI_SDK_BIN}/${target_name})

  if(MSVC AND "${CMAKE_BUILD_TYPE}" STREQUAL "DEBUG")
    set(_bin_path ${_bin_path}_d)
  endif()

  add_test(${test_name} ${_bin_path} ${ARG_ARGUMENTS})

  # Be nice with Visual Studio users:
  set_target_properties(${target_name}
    PROPERTIES
      FOLDER "tests")

  set_tests_properties(${test_name} PROPERTIES
    TIMEOUT ${ARG_TIMEOUT}
  )

  # HACK for apple until the .dylib problems are fixed...
  if(APPLE)
    set_tests_properties(${test_name} PROPERTIES
      ENVIRONMENT "DYLD_LIBRARY_PATH=${QI_SDK_DIR}/${QI_SDK_LIB};DYLD_FRAMEWORK_PATH=${QI_SDK_DIR}"
    )
  endif()
endfunction()
