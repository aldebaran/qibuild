cmake_minimum_required(VERSION 2.8)
project(compile_data)

find_package(qibuild)

# Create a executable named compile_data
# with the source file: main.cpp
qi_create_bin(compiler "compiler.cpp")
set(_in "${CMAKE_CURRENT_SOURCE_DIR}/foo.in")
set(_out "${CMAKE_CURRENT_BINARY_DIR}/foo.out")

if(FAIL_COMPILER)
  add_definitions(-DFAIL_COMPILER)
endif()

set_source_files_properties(${_out}
  PROPERTIES
    GENERATED TRUE)

get_target_property(_compiler compiler
  LOCATION_${CMAKE_BUILD_TYPE})
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/compile_data.in.cmake
               ${CMAKE_CURRENT_BINARY_DIR}/compile_data.cmake
               @ONLY)

install(SCRIPT ${CMAKE_CURRENT_BINARY_DIR}/compile_data.cmake)

qi_install_data(
  "${CMAKE_CURRENT_BINARY_DIR}/foo.out")
