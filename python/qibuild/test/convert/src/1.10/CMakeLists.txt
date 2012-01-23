cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)
project(foo_1_10)
include(${CMAKE_CURRENT_SOURCE_DIR}/bootstrap.cmake)
create_lib(world world.cpp)
stage_lib(world WORLD ${CMAKE_CURRENT_SOURCE_DIR})

create_bin(hello hello.cpp)
use_lib(hello WORLD)

