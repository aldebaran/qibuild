##
## This is a nice install example
##

cmake_minimum_required(VERSION 2.8)
include(qibuild.cmake)
project(install_example)

qi_install_data(foo/foo.data)
