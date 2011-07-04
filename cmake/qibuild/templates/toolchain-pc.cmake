## Copyright (C) 2011 Aldebaran Robotics

# Toolchain file to be passed to cmake, using:
# cmake -DCMAKE_TOOLCHAIN_FILE=/path/to/sdk/toolchain-pc.cmake
# (or the "use a toolchain file" option from the cmake-gui)

# Warning ! This file is NOT usable for cross-compilation

# Set _SDK_ROOT_DIR to the dirname of this file (/path/to/sdk)
get_filename_component(_SDK_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)

# Librairies are looked for in /path/to/sdk/lib,
# headers in /path/to/sdk/include, and so on.
set(CMAKE_FIND_ROOT_PATH "${_SDK_ROOT_DIR}")

# Path to the qibuild framework:
list(APPEND CMAKE_MODULE_PATH "${_SDK_ROOT_DIR}/share/cmake")

# Enable usage of the qi_ cmake functions:
include(qibuild/general)

# Enable backward compatibility:
include(qibuild/compat/compat)

# Force 32 bits compilation even if we are on a
# 64 bits OS:
set(CMAKE_OSX_ARCHITECTURES i386 CACHE INTERNAL "" FORCE)

# By default, generate output of the compilation in this SDK.
# This is useful for naoqi to find the module you've just compiled
set(QI_SDK_DIR "${_SDK_ROOT_DIR}" CACHE INTERNAL "" FORCE)
