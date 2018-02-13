 cmake_minimum_required(VERSION 2.8)
project(foo C)
find_package(qibuild)
qi_create_bin(foo main.c)

