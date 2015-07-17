cmake_minimum_required(VERSION 2.8)
project(usefoopymodule)
find_package(qibuild)

find_program(PYTHON_EXECUTABLE "python")
qi_add_test(test_usefoopymodule
  ${PYTHON_EXECUTABLE} ARGUMENTS "${CMAKE_CURRENT_SOURCE_DIR}/test.py")

