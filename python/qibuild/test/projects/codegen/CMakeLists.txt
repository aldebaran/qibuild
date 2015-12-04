cmake_minimum_required(VERSION 2.8)
project(foo)

find_package(qibuild)

set(_out ${CMAKE_BINARY_DIR}/main.cpp)
set(_cmd
  COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/gen.py
          ${CMAKE_CURRENT_SOURCE_DIR}/main.in.cpp
          ${_out}
          DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/gen.py
)
if(FAIL)
  list(APPEND _cmd "--fail")
endif()

qi_generate_src(${_out} SRC main.in.cpp COMMAND ${_cmd})
qi_create_bin(test_foo ${_out})
