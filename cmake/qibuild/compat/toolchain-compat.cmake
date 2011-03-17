## Copyright (C) 2011 Aldebaran Robotics

# Toolchain file to be passed to cmake, using
# cmake -DCMAKE_TOOLCHAIN_FILE=/path/to/sdk/toolchain-pc.cmake


# Set _ROOT_DIR to the dirname of this file (/path/to/sdk)
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)

# Librairies are looked for in /path/to/sdk/lib,
# headers in /path/to/include, and so on.
set(CMAKE_FIND_ROOT_PATH "${_ROOT_DIR}")

# To be able to do +include(qibuild/general.cmake)+.
list(APPEND CMAKE_MODULE_PATH "${_ROOT_DIR}/share/cmake")
