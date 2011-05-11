## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild Tests
# ==============
#
# This CMake module provides function to interface gtest with ctest.


set(_TESTS_RESULTS_FOLDER "${CMAKE_SOURCE_DIR}/build-tests/results" CACHE INTERNAL "" FORCE)


#! Add a test using a binary that was created by qi_create_bin
# The only difference with the CMake method add_test() is that qi_add_test will deal with
# the fact that the the binary is in the sdk/bin directory, and than it is named
# with _d on visual studio.
# \param:TIMETOUT The timeout of the test
# \group:ARGUMENTS Arguments to pass to add_test
function(qi_add_test test_name target_name)
  cmake_parse_arguments(ARG "" "TIMEOUT;ARGUMENTS" "" ${ARGN})

  if(NOT ARG_TIMEOUT)
    set(ARG_TIMEOUT 20)
  endif()

  if(MSVC)
    set(_bin_path ${QI_SDK_DIR}/${target_name})
  else()
    set(_bin_path ${QI_SDK_DIR}/${QI_SDK_BIN}/${target_name})
  endif()

  if(MSVC AND ${CMAKE_BUILD_TYPE} STREQUAL "DEBUG")
    set(_bin_path ${_bin_path}_d)
  endif()

  add_test(${test_name} ${_bin_path} ${ARG_ARGUMENTS})

  set_target_properties(${target_name}
    PROPERTIES
      FOLDER "tests")

  set_tests_properties(${test_name} PROPERTIES
    TIMEOUT ${ARG_TIMEOUT}
  )

  # HACK for apple until the .dylib problems are fixed...
  if(APPLE)
    set_tests_properties(${test_name} PROPERTIES
      ENVIRONMENT "DYLD_LIBRARY_PATH=${QI_SDK_DIR}/${QI_SDK_LIB}"
    )
  endif()
endfunction()



#! This compiles and add_test's a CTest test that uses gtest.
# (so that the test can be run by CTest)
# When run, the CTest test outputs an xUnit xml file in
# ${CMAKE_SOURCE_DIR}/test-results/${test_name}.xml
# The name of the test will always be the name of the target.
#
# \flag:NO_ADD_TEST Do not call add_test, just create the binary
# \param:TIMEOUT The timeout of the test
# \group:SRC Sources
# \group:DEPENDS Dependencies to pass to use_lib
# \group:ARGUMENTS Arguments to pass to add_test (to your test program)
function(qi_create_gtest name)
  # create tests_results folder if it does not exist
  file(MAKE_DIRECTORY "${_TESTS_RESULTS_FOLDER}")
  cmake_parse_arguments(ARG "NO_ADD_TEST" "TIMEOUT" "SRC;DEPENDS;ARGUMENTS" ${ARGN})

  # First, create the target
  qi_create_bin(${name} SRC ${ARG_SRC} NO_INSTALL)
  qi_use_lib(${name} ${ARG_DEPENDS})

  # Build a correct xml output name
  set(_xml_output "${_TESTS_RESULTS_FOLDER}/${name}.xml")

  if (WIN32)
    string(REPLACE "/" "\\\\" xml_output ${_xml_output})
  endif()

  # Call qi_add_test with correct arguments:
  qi_add_test(${name} ${name}
    TIMEOUT ${ARG_TIMEOUT}
    ARGUMENTS --gtest_output=xml:${_xml_output} ${ARG_ARGUMENTS}
  )
endfunction()
