 cmake_minimum_required(VERSION 2.8)
project(hello C)
find_package(qibuild)
qi_create_bin(hello main.c)

