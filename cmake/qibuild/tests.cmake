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
  if (DEFINED QI_WITH_TESTS AND NOT QI_WITH_TESTS)
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
  if (DEFINED QI_WITH_TESTS AND NOT QI_WITH_TESTS)
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
    GTEST
  )
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
  if (DEFINED QI_WITH_TESTS AND NOT QI_WITH_TESTS)
    qi_persistent_set(QI_${name}_TARGET_DISABLED TRUE)
    return()
  endif()
  cmake_parse_arguments(ARG "" "TIMEOUT" "SRC;DEPENDS;ARGUMENTS" ${ARGN})
  set(_src ${ARG_UNPARSED_ARGUMENTS} ${ARG_SRC})
  set(_deps ${ARG_DEPENDS})
  set(_args ${ARG_ARGUMENTS})

  if(NOT ARG_TIMEOUT)
    set(ARG_TIMEOUT 120)
  endif()

  # create the executable:
  qi_create_bin(${name} ${_src} NO_INSTALL DEPENDS ${_deps})
  set(_bin_path ${QI_SDK_DIR}/${QI_SDK_BIN}/${name})

  if(WIN32 AND "${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
    set(_bin_path ${_bin_path}_d)
  endif()
  if(WIN32)
    set(_bin_path "${_bin_path}.exe")
  endif()
  file(TO_NATIVE_PATH ${_bin_path} _bin_path)

  set(_perf_dir ${CMAKE_BINARY_DIR}/perf-results)
  file(MAKE_DIRECTORY ${_perf_dir})

  set(_args "--output" ${_perf_dir}/${name}.xml)

  qi_add_test(${name} ${name}
    TIMEOUT ${ARG_TIMEOUT}
    ARGUMENTS ${_args}
    PERF
  )


endfunction()

#! Add a test using a binary that was created by :cmake:function:`qi_create_bin`
#
# This calls ``add_test()`` with the same arguments but:
#
# * We look for the binary in sdk/bin, as a target, or an external
#   package, and we know there is a``_d `` when using Visual Studio on debug
# * We set a ``tests`` folder property
# * We make sure necessary environment variables are set on mac
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
  cmake_parse_arguments(ARG "PERF;NIGHTLY;GTEST" "TIMEOUT" "ARGUMENTS" ${ARGN})

  if(DEFINED QI_WITH_TESTS AND NOT QI_WITH_TESTS)
    return()
  endif()

  if(ARG_NIGHTLY AND NOT ${QI_WITH_NIGHTLY_TESTS})
    return()
  endif()

  if(ARG_PERF AND NOT ${QI_WITH_PERF_TESTS})
    return()
  endif()

  if(NOT ARG_TIMEOUT)
    set(ARG_TIMEOUT 20)
  endif()
  # Validate target_name. We expect one of:
  # - A target name expected to be an executable with standard path.
  # - A relative or absolute path to an existing binary.
  # - A path that leads to an executable when using find_program
  # - A package name providing a ${name}_EXECUTABLE variable.
  if(TARGET ${target_name})
    set_target_properties(${target_name} PROPERTIES FOLDER "tests")
    set(_bin_path ${QI_SDK_DIR}/${QI_SDK_BIN}/${target_name})

    if(MSVC AND "${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
      set(_bin_path ${_bin_path}_d)
    endif()
  else()
    set(_executable "${target_name}")
    # In case we already used find_program, or used
    # a relative path, avoid searching for it twice
    get_filename_component(_bin_path ${_executable} ABSOLUTE)
    if(NOT EXISTS  ${_bin_path})
      # look for it
      find_program(_executable "${target_name}")
      if(NOT _executable)
        # Try package
        find_package(${target_name})
        string(TOUPPER ${target_name}_EXECUTABLE _executable)
        if(NOT ${_executable}) # If expects a variable name not content
          qi_error("${target_name} is not a target, an existing file or a package providing ${target_name}_EXECUTABLE")
        endif()
        set(_bin_path ${${_executable}})
      endif()
    endif()
  endif()

  set(_cmd ${_bin_path} ${ARG_ARGUMENTS})

  set( _qi_add_test_args "--name" ${test_name})
  list(APPEND _qi_add_test_args "--output" ${CMAKE_BINARY_DIR}/qitest.json)

  if (ARG_GTEST)
    list(APPEND _qi_add_test_args "--gtest")
  endif()

  if (ARG_TIMEOUT)
    list(APPEND _qi_add_test_args "--timeout" ${ARG_TIMEOUT})
  endif()

  if (ARG_NIGHTLY)
    list(APPEND _qi_add_test_args "--nightly")
  endif()

  if (ARG_PERF)
    list(APPEND _qi_add_test_args "--perf")
  endif()
  list(APPEND _qi_add_test_args "--")

  set(_qi_add_test_args ${_qi_add_test_args} ${_cmd})

  qi_run_py_script("${qibuild_DIR}/qi_add_test.py"
    ARGUMENTS ${_qi_add_test_args}
  )
  
  if(TARGET "${target_name}")
    install(TARGETS "${target_name}" DESTINATION "bin" COMPONENT "test")
  endif()

endfunction()
