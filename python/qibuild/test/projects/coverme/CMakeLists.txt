cmake_minimum_required(VERSION 2.8)
project(coverme)

find_package(qibuild)

include_directories(".")
qi_create_lib(foo "foo.h" "foo.cpp")
qi_stage_lib(foo)

qi_create_test(test_foo "test.cpp")
qi_use_lib(test_foo foo)
