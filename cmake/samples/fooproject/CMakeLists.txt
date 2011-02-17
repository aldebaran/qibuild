cmake_minimum_required(VERSION 2.8)
include("qibuild.cmake")
project(fooproject)

enable_testing()

add_subdirectory(foo)
add_subdirectory(foo/test)
