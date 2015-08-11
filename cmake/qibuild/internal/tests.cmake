## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(_qi_add_test_internal test_name target_name)
  cmake_parse_arguments(ARG
    "NO_INSTALL;NO_ADD_TEST;NIGHTLY;PERF_TEST;GTEST_TEST;GMOCK_TEST"
    "TIMEOUT;WORKING_DIRECTORY"
    "SRC;DEPENDS;SUBMODULE;ARGUMENTS;ENVIRONMENT" ${ARGN})

  set(_srcs ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS})

  if(NOT QI_WITH_TESTS)
    set(_should_return TRUE)
  endif()

  if(ARG_NIGHTLY AND NOT QI_WITH_NIGHTLY_TESTS)
    set(_should_return TRUE)
  endif()

  if(ARG_PERF_TEST AND NOT QI_WITH_PERF_TESTS)
    set(_should_return TRUE)
  endif()

  if(ARG_NO_ADD_TEST)
    qi_deprecated("NO_ADD_TEST is deprecated, use qi_create_test_helper instead")
    qi_create_test_helper(${target_name} ${_srcs})
    set(_deps ${ARG_DEPENDS})
    if(ARG_GTEST_TEST)
      list(APPEND _deps GTEST GTEST_MAIN)
    endif()
    if(ARG_GMOCK_TEST)
      list(APPEND _deps GMOCK GMOCK_MAIN)
    endif()
    if(TARGET ${target_name})
      qi_use_lib(${target_name} ${_deps})
    endif()
    return()
  endif()

  if(NOT ARG_TIMEOUT)
    set(ARG_TIMEOUT 20)
  endif()

  if(_should_return)
    return()
  endif()

  if(_srcs)
    set(_deps ${ARG_DEPENDS})
    set(_submodules ${ARG_SUBMODULE})
    if(ARG_GTEST_TEST)
      list(APPEND _deps GTEST GTEST_MAIN)
    endif()
    if(ARG_GMOCK_TEST)
      list(APPEND _deps GMOCK GMOCK_MAIN)
    endif()
    # Using NO_INSTALL because we don't want to be in the 'runtime'
    # component like the other binaries
    qi_create_bin(${target_name} SRC ${_srcs} DEPENDS ${_deps} SUBMODULE ${_submodules} NO_INSTALL)
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
    if(WIN32)
      set(_bin_path "${_bin_path}.exe")
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

  if(ARG_WORKING_DIRECTORY)
    list(APPEND _qi_add_test_args "--working-directory" ${ARG_WORKING_DIRECTORY})
  endif()

  if(ARG_GTEST_TEST)
    list(APPEND _qi_add_test_args "--gtest")
  endif()

  if(ARG_GMOCK_TEST)
    list(APPEND _qi_add_test_args "--gtest")
  endif()

  if(ARG_TIMEOUT)
    list(APPEND _qi_add_test_args "--timeout" ${ARG_TIMEOUT})
  endif()

  if(ARG_NIGHTLY)
    list(APPEND _qi_add_test_args "--nightly")
  endif()

  foreach(_keyval ${ARG_ENVIRONMENT})
    string(REPLACE "=" ";" _splitted ${_keyval})
    list(LENGTH _splitted _len)
    if(${_len} EQUAL 2)
      list(GET _splitted 0 _key)
      list(GET _splitted 1 _val)
      list(APPEND _qi_add_test_args "--env" ${_keyval})
    else()
      message(FATAL_ERROR "Expecting an expression looking like <key>=<value>,
                           got ${_keyval} instead")
    endif()
  endforeach()

  if(ARG_PERF_TEST)
    list(APPEND _qi_add_test_args "--perf")
  endif()
  list(APPEND _qi_add_test_args "--")

  set(_qi_add_test_args ${_qi_add_test_args} ${_cmd})

  file(APPEND ${CMAKE_BINARY_DIR}/qitest.cmake "${_qi_add_test_args}\n")

  if(NOT ARG_NO_INSTALL)
    if(TARGET "${target_name}")
      install(TARGETS "${target_name}" DESTINATION "bin" COMPONENT "test")
    endif()
  endif()
endfunction()
