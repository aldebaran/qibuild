cmake_minimum_required(VERSION 2.8)
project(fake-gtest)

find_package(qibuild)

include_directories(".")
qi_create_lib(gtest src/gtest.cc)
qi_stage_lib(gtest)
qi_create_lib(gtest_main src/main.cc)
qi_stage_lib(gtest_main)
qi_install_header(fakegtest/gtest.h KEEP_RELATIVE_PATHS)
