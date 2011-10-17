cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)

project(world)

include("${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake")

include_directories(".")

qi_create_lib(world SHARED
  world/world.h
  world/world.cpp)

qi_create_lib(bar STATIC INTERNAL
  bar/bar.h
  bar/bar.cpp)

qi_create_lib(myplugin SHARED SUBFOLDER "word"
  plugin.cpp
  plugin.h)


qi_install_header(world/world.h SUBFOLDER world)
qi_install_header(bar/bar.h KEEP_RELATIVE_PATHS)

qi_stage_lib(world)
qi_stage_lib(bar)

qi_stage_cmake(cmake/foo-config.cmake)

find_package(foo REQUIRED)
foo()
