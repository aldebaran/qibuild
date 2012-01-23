cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)
project(foo)
include(qibuild.cmake)
qi_create_lib(world world.cpp)
qi_stage_lib(world)

qi_create_bin(hello hello.cpp)
qi_use_lib(hello WORLD)

