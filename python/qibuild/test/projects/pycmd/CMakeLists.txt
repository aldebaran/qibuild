cmake_minimum_required(VERSION 2.8)
project(pycmd)
find_package(qibuild)

if(FAIL)
  qi_run_py_cmd("import sys; sys.exit(1)")
endif()

qi_run_py_script(${CMAKE_SOURCE_DIR}/test.py
  ARGUMENTS "hello" "world"
  OUTPUT_VARIABLE _out
  OUTPUT_STRIP_TRAILING_WHITESPACE)

set(_expected "Hello, World!")
if(NOT ${_out} STREQUAL ${_expected})
  qi_error("actual: ${_out}
            expected: ${_expected}")
endif()

set(_to_write "Written from Python\\n")
qi_run_py_cmd("
fp = open('${CMAKE_BINARY_DIR}/test.txt', 'w')
fp.write('${_to_write}')
fp.close()
")

qi_run_py_cmd("
fp = open('${CMAKE_BINARY_DIR}/test.txt', 'r')
print fp.read()
"
  OUTPUT_VARIABLE _out
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

if(NOT "${_out}" STREQUAL "Written from Python")
  qi_error("actual: ${_out}
            expected: ${_to_write}")
endif()

qi_run_py_cmd("import qibuild")

