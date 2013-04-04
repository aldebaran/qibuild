cmake_minimum_required(VERSION 2.8)
project(runtests)

find_package(qibuild)
enable_testing()
qi_create_test(ok ok.cpp)
qi_create_test(fail fail.cpp)
qi_create_test(segfault segfault.cpp)
qi_create_test(timeout timeout.cpp TIMEOUT 1)

