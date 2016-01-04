cmake_minimum_required(VERSION 2.8)
project(spam)

find_package(qibuild)

qi_create_bin(spam "main.cpp")
