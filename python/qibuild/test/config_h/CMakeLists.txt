cmake_minimum_required(VERSION 2.8)
project(foo)
find_package(qibuild)

enable_testing()


set(ANSWER 42)
qi_create_config_h(_out ${CMAKE_CURRENT_SOURCE_DIR}/config.in.h foo/config.h)
qi_create_bin(foo main.cpp)
message(STATUS "_out: ${_out}")

