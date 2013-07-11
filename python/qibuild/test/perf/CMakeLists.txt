cmake_minimum_required(VERSION 2.8)
project(perf)

find_package(qibuild)

qi_create_perf_test(perf_spam SRC main.cpp TIMEOUT 42)
qi_create_perf_test(perf_eggs SRC main.cpp ARGUMENTS "--foo" "bar")
qi_create_perf_test(perf_timeout SRC timeout.cpp TIMEOUT 1)
qi_create_perf_test(perf_segv SRC segv.cpp)
