cmake_minimum_required(VERSION 2.8)
project(gtestuser)

find_package(qibuild)

qi_create_gtest(test_foo "test.cpp")
