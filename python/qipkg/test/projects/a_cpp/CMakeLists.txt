cmake_minimum_required(VERSION 2.8)

project(a_cpp)
find_package(qibuild)

qi_create_lib(foo foo.cpp)
