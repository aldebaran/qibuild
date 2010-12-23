cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)

project(hello)

include("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")


qi_create_bin(hello "main.cpp")
qi_use_lib(hello world)
