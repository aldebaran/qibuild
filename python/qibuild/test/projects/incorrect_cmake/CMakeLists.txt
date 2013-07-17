cmake_minimum_required(VERSION 2.8)
# find_package should be after project
# because the toolchain file is read only
# after project() has been called
find_package(qibuild)
project(incorrect)
