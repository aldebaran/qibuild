cmake_minimum_required(VERSION 2.8)
project(cross C)

add_library(foo SHARED foo.c)
add_library(bar SHARED bar.c)

target_link_libraries(bar foo)
install(TARGETS bar
  DESTINATION lib)
