cmake_minimum_required(VERSION 2.8)
project(fooproject)
find_package(qibuild)

# Add a subdirectory containing the foo library
add_subdirectory(libfoo)


# Use it in the bar project.
qi_create_bin(bar main.cpp)
qi_use_lib(bar foo)


