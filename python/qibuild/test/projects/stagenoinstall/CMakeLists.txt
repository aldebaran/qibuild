cmake_minimum_required(VERSION 2.8)
project(stagenoinstall)

find_package(qibuild)

qi_create_lib(foo "foo.c" NO_INSTALL)
qi_stage_lib(foo)

find_package(FOO)
message(STATUS "FOO_DIR: ${FOO_DIR}")
qi_create_bin(bar bar.c)
qi_use_lib(bar FOO)
