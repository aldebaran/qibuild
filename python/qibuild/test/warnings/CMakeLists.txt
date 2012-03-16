cmake_minimum_required(VERSION 2.8)
project(warnings)

find_package(qibuild)
qi_sanitize_compile_flags()

qi_create_bin(foo "main.cpp")

