cmake_minimum_required(VERSION 2.8)
project(perf)

find_package(qibuild)

qi_create_perf_test(perf_spam SRC main.cpp)
qi_create_perf_test(perf_eggs SRC main.cpp ARGUMENTS "--foo" "bar")
