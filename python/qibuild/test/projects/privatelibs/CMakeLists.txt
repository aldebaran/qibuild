cmake_minimum_required(VERSION 2.8)
project(test_privaste_libs C)

find_package(qibuild)
include_directories(".")

qi_create_lib(foo_private foo_private.c INTERNAL)
qi_stage_lib(foo_private)

qi_create_lib(foo_public foo_public.c)
qi_use_lib(foo_public foo_private)
# Since foo_public.h contains no private symbols,
# we can stage the public lib with no dependency
# at all
qi_stage_lib(foo_public DEPENDS "")

qi_create_bin(bar bar.c)
qi_use_lib(bar foo_public)

