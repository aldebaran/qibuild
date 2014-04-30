# CMake file for b_ext

cmake_minimum_required(VERSION 2.8)
project(b_ext)
find_package(qibuild)

qi_create_python_ext(_b b.c)
