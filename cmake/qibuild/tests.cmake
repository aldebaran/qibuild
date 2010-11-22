##
## tests.cmake
## Login : <ctaf@cgestes-de>
## Started on  Tue Oct 20 11:50:53 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Cedric GESTES
##

function(configure_tests _name)
  include("${CMAKE_CURRENT_SOURCE_DIR}/${_name}")
endfunction()

set(_TESTS_RESULTS_FOLDER "${CMAKE_BINARY_DIR}/tests-results" CACHE INTERNAL "" FORCE)
# create tests_results folder if it does not exist
file(MAKE_DIRECTORY "${_TESTS_RESULTS_FOLDER}")

################################################################################
#
# This compiles and add_test's a C++ test that uses gtest.
# When run, the C++ test outputs a xUnit xml file in
#   CMAKE_SOURCE_DIR/test_name.xml.
#
# SRC: sources
# DEPENDENCIES: dependencies to pass to use_lib
# ARGUMENTS: arguments to pass to add_test (to your test program)
# TIMEOUT: the timeout of the test
# NO_ADD_TEST: do not call add_test, just create the binary
#
# Usage:
# create_gtest("test_name" SRC mytest0.cpp mytest1.cpp
#                          DEPENDENCIES MY_LIB_TO_TEST0 MY_LIB_TO_TEST1
#                          TIMEOUT 45)
################################################################################
function(create_gtest _name)
  if (NOT TARGET "autotest")
    add_custom_target("autotest")
  endif()
  debug("create_gtest: ${_name} is going to be built and add_test'ed.")

  # Retrieve src and dependencies arguments.
  subargs_parse_args("SRC"          "DEPENDENCIES;ARGUMENTS;TIMEOUT" _src          _arg1 ${ARGN})
  subargs_parse_args("DEPENDENCIES" "SRC;ARGUMENTS;TIMEOUT"          _dependencies _arg2 ${_arg1})
  subargs_parse_args("ARGUMENTS"    "DEPENDENCIES;SRC;TIMEOUT"       _arguments    _arg3 ${_arg2})
  subargs_parse_args("TIMEOUT"      "DEPENDENCIES;SRC;ARGUMENTS"     _timeout      _arg4 ${_arg3})
  parse_is_options(_args4 NO_ADD_TEST _no_add_test ${_arg3})

  if(NOT _timeout)
    set(_timeout 20)
  endif()

  # Create the binary test, link with dependencies.
  if (BUILD_TESTS)
    create_bin("${_name}_bin" ${_src} NO_INSTALL)
  else()
    create_bin("${_name}_bin" EXCLUDE_FROM_ALL ${_src} NO_INSTALL)
  endif()
  add_dependencies("autotest" "${_name}_bin")
  use_lib("${_name}_bin" ${_dependencies})

  if (_no_add_test)
    return()
  endif()

  # use sdk trampoline (.bat on windows) to set all environment variables correctly.
  if(WIN32)
    gen_sdk_trampoline("${_name}_bin" "${_name}.bat")
    _add_gtest("${_name}.bat" ${_name} ARGUMENTS ${_arguments})
  else()
    gen_sdk_trampoline("${_name}_bin" ${_name})
    _add_gtest(${_name} ${_name} ARGUMENTS ${_arguments})
  endif()
  set_tests_properties(${_name} PROPERTIES TIMEOUT ${_timeout})
endfunction()

################################################################################
#
# Tiny wrapper around add_test in order to use nosetests to run python tests.
# Xml output (test_name.xml) will be in build/tests_results
# A Python test timeout is 20 seconds by default.
# An additional parameter can be set to change timeout
#
# Usage:
# add_python_test(MyTest "mytest.py")
#
################################################################################
function(add_python_test _name _pythonFile)

  subargs_parse_args("TIMEOUT"   "ARGUMENTS" _timeout   _arg1 ${ARGN})
  subargs_parse_args("ARGUMENTS" "TIMEOUT"   _arguments _arg2 ${_arg1})

  #Nosetests is required to do testing !
  if(NOT RUNNOSETESTS_EXECUTABLE)
    use(PYTHON-TOOLS)
    gen_nosetests_script()
    find(RUNNOSETESTS)
  endif()

  set(xml_output_name "${_TESTS_RESULTS_FOLDER}/${_name}.xml")

  add_test(${_name} ${RUNNOSETESTS_EXECUTABLE} ${_pythonFile} --nologcapture --nocapture --with-xunit --xunit-file=${xml_output_name} ${_arguments})

  if(NOT _timeout)
    set(_timeout 20)
  endif()
  set_tests_properties(${_name} PROPERTIES TIMEOUT ${_timeout})
endfunction()


################################################################################
#
# Tiny wrapper around add_test that defines the gtest xml output path.
# Xml output (test_name.xml) will be in build/tests_results
#
# Usage:
# _add_gtest("executable_name" "test_name")
#
################################################################################
function(_add_gtest _executable_name _test_name)
  subargs_parse_args("ARGUMENTS" ""   _arguments _arg2 ${ARGN})

  set(xml_output_name "${_TESTS_RESULTS_FOLDER}/${_test_name}.xml")

  # Replaces / for windows, and remove .bat from xml name:
  if (WIN32)
    string(REPLACE "/" "\\\\" xml_output_name ${xml_output_name})
  endif()

  # Add gtest for ctest with xml output file.
  add_test(${_test_name} ${SDK_DIR}/bin/${_executable_name} --gtest_output=xml:${xml_output_name} ${_arguments})
endfunction()

