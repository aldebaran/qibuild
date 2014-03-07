cmake_minimum_required(VERSION 2.8)
project(test_stage_lib_user)

find_package(qibuild)
include_directories(".")

find_program(_python_executable
    NAMES python2 python python.exe
    NO_CMAKE_PREFIX_PATH)
  if (NOT _python_executable)
    qi_error("needs python executable in PATH")
  endif()

find_package(nodep)
find_package(dlopenworlduser)
add_custom_target(run_nodep ALL COMMAND ${_python_executable} ${NODEP_EXECUTABLE})
add_custom_target(run_dlopenworlduser ALL COMMAND ${_python_executable} ${DLOPENWORLDUSER_EXECUTABLE})
