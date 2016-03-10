cmake_minimum_required(VERSION 2.8)
project(libsubfolder C)

find_package(qibuild)

qi_create_lib(foo foo.c SHARED SUBFOLDER foo)

if("${CMAKE_SYSTEM_NAME}" STREQUAL "Darwin")
  set_target_properties(foo
    PROPERTIES
      INSTALL_NAME_DIR "@loader_path/../lib/foo")
endif()
qi_stage_lib(foo)

qi_create_bin(bar bar.c NO_RPATH)
qi_use_lib(bar foo)
if("${CMAKE_SYSTEM_NAME}" STREQUAL "Linux")
  set_target_properties(bar
    PROPERTIES
      INSTALL_RPATH "\$ORIGIN/../lib/foo")
endif()
