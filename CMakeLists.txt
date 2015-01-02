## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# You can use this CMake file to install qibuild on your
# system, if you want to, but this will only install
# the CMake wrapper.
# You really should use the setup.py file instead

cmake_minimum_required(VERSION 2.8)

project(qiBuild NONE)

# Install CMake code where it belongs
set(_qibuild_cmake_install_dest)

if(UNIX)
  set(_qibuild_cmake_install_dest
    ${CMAKE_INSTALL_PREFIX}/share/cmake/
  )
else()
  # No need to try /usr/local/share/
  # on windows:
  set(_qibuild_cmake_install_dest
    ${CMAKE_ROOT}/Modules
  )
endif()

install(
  DIRECTORY
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/qibuild
  DESTINATION
    "${_qibuild_cmake_install_dest}"
)
