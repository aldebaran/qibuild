cmake_minimum_required(VERSION 2.8)
project(footool)

find_package(qibuild)

qi_create_bin(footool "footool.cpp" SUBFOLDER tools)
qi_stage_bin(footool)

