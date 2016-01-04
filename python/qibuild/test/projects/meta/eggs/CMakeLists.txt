cmake_minimum_required(VERSION 2.8)
project(eggs)

find_package(qibuild)

qi_create_bin(eggs "main.cpp")
