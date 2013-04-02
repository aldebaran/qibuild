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


set(_TESTS_RESULTS_FOLDER "${CMAKE_BINARY_DIR}/test-results" CACHE INTERNAL "" FORCE)


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
  if (DEFINED BUILD_TESTS AND NOT BUILD_TESTS)
    qi_debug("Test(${name}) disabled by BUILD_TESTS=OFF")
    qi_persistent_set(QI_${name}_TARGET_DISABLED TRUE)
    return()
  endif()
  cmake_parse_arguments(ARG "NIGHTLY" "TIMEOUT" "SRC;DEPENDS;ARGUMENTS" ${ARGN})
  if(ARG_NIGHTLY AND NOT ${QI_NIGHTLY_TESTS})
    return()
  endif()
  qi_create_bin(${name} SRC ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS} NO_INSTALL)
  if(ARG_DEPENDS)
    qi_use_lib(${name} ${ARG_DEPENDS})
  endif()
  qi_add_test(${name} ${name}
    TIMEOUT ${ARG_TIMEOUT}
    ARGUMENTS ${ARG_ARGUMENTS}
  )
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
  if (DEFINED BUILD_TESTS AND NOT BUILD_TESTS)
    qi_debug("Test(${name}) disabled by BUILD_TESTS=OFF")
    qi_persistent_set(QI_${name}_TARGET_DISABLED TRUE)
    return()
  endif()

  # create tests_results folder if it does not exist
  file(MAKE_DIRECTORY "${_TESTS_RESULTS_FOLDER}")
  cmake_parse_arguments(ARG "NO_ADD_TEST;NIGHTLY" "TIMEOUT" "SRC;DEPENDS;ARGUMENTS" ${ARGN})
  if(ARG_NIGHTLY AND NOT ${QI_NIGHTLY_TESTS})
    return()
  endif()

  # First, create the target
  qi_create_bin(${name} SRC ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS} NO_INSTALL)
  qi_use_lib(${name} GTEST GTEST_MAIN ${ARG_DEPENDS})

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

  if (ARG_NO_ADD_TEST)
    return()
  endif()
  qi_add_test(${name} ${name}
    TIMEOUT ${ARG_TIMEOUT}
    ARGUMENTS ${_args}
  )
endfunction()

#! Add a test using a binary that was created by :cmake:function:`qi_create_bin`
#
# This calls ``add_test()`` with the same arguments but:
#
#  * We look for the binary in sdk/bin, as a target, or an external
#    package, and we know there is a _d when using Visual Studio
#  * We set a 'tests' folder property
#  * We make sure necessary environment variables are set on mac
#
# This is a low-level function, you should rather use
# :cmake:function:`qi_create_test` or :cmake:function:`qi_create_gtest` instead.
#
# \arg:test_name The name of the test
# \arg:target_name The name of the binary to use. It can be a target name,
#                  an absolute or relative path to an existing file,
#                  or a package name providing a ${name}_EXECUTABLE variable.
# \param:TIMEOUT The timeout of the test
# \flag: NIGHTLY: only compiled (and thus run) if QI_NIGHTLY_TESTS is ON
# \group:ARGUMENTS Arguments to be passed to the executable
function(qi_add_test test_name target_name)
  cmake_parse_arguments(ARG "NIGHTLY" "TIMEOUT" "ARGUMENTS" ${ARGN})
  if(ARG_NIGHTLY AND NOT ${QI_NIGHTLY_TESTS})
    return()
  endif()

  if(NOT ARG_TIMEOUT)
    set(ARG_TIMEOUT 20)
  endif()
  # Validate target_name. We expect one of:
  # - A target name expected to be an executable with standard path.
  # - A relative or absolute path to an existing binary.
  # - A package name providing a ${name}_EXECUTABLE variable.
  if(TARGET ${target_name})
    set(_bin_path ${QI_SDK_DIR}/${QI_SDK_BIN}/${target_name})

    if(MSVC AND "${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
      set(_bin_path ${_bin_path}_d)
    endif()

    add_test(${test_name} ${_bin_path} ${ARG_ARGUMENTS})
    set_target_properties(${target_name} PROPERTIES FOLDER "tests")
  else()
    # Just in case user specified a relative path:
    get_filename_component(_full_path ${target_name} ABSOLUTE)
    if(NOT EXISTS ${_full_path})
      # Try package
      find_package(${target_name})
      string(TOUPPER ${target_name}_EXECUTABLE _executable)
      if(NOT ${_executable}) # If expects a variable name not content
        qi_error("${target_name} is not a target, an existing file or a package providing ${target_name}_EXECUTABLE")
      endif()
      set(_full_path ${${_executable}})
    endif()
    add_test(${test_name} ${_full_path} ${ARG_ARGUMENTS})
  endif()

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
