cmake_minimum_required(VERSION 2.8)
project(runtests)

find_package(qibuild)
enable_testing()
qi_create_test(one main.cpp)
qi_create_test(two main.cpp)
qi_create_test(three main.cpp)
qi_create_test(four main.cpp)
