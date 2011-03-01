cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)

project(world)

include("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
qi_create_lib(world SHARED
  SRC world/world.h
      world/world.cpp)

qi_install_header(world world/world.h)

qi_stage_lib(world)
