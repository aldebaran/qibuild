cmake_minimum_required(VERSION 2.8)

# Give a name to the project.
project(swig-example)

# You need this to find the QiBuild CMake framework
find_package(qibuild)

include(qibuild/swig/python)

qi_swig_wrap_python(eggs eggs.i
  SRC eggs.cpp eggs.hpp)
