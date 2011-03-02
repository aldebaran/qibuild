cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)

project(hello)

include("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")


qi_create_bin(hello "main.cpp")
qi_use_lib(hello world)

enable_testing()
# Add a test that just runs hello without arguments
qi_add_test(zero_test hello)

# Use the foo file staged by world:
find_package(foo REQUIRED)
foo()
