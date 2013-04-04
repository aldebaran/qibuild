cmake_minimum_required(VERSION 2.8)
project(debugme)

find_package(qibuild)

# Create a executable named debugme
# with the source file: main.cpp
qi_create_bin(debugme "main.cpp")
