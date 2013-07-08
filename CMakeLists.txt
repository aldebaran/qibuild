## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# You can use this CMake file to install qibuild on your
# system, if you want to, but please not that you
# won't be able to uninstall it afterward.
# It is advised you use the ./install-qibuild scripts instead, or the
# packages provided by Aldebaran

cmake_minimum_required(VERSION 2.8)

project(qiBuild NONE)

option(QIBUILD_CMAKE_ONLY "Only install the CMake framework" OFF)

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

if(QIBUILD_CMAKE_ONLY)
  return()
endif()

option(WITH_DOCS "Build man pages" ON)

find_program(PYTHON_EXECUTABLE NAMES python2 python python.exe
  PATHS
    [HKEY_LOCAL_MACHINE\\SOFTWARE\\Python\\PythonCore\\2.6\\InstallPath]
    [HKEY_LOCAL_MACHINE\\SOFTWARE\\Python\\PythonCore\\2.7\\InstallPath]
)

if(NOT PYTHON_EXECUTABLE)
  message(STATUS
    "
    Could not find python executable.

    Please check your setup.

    "
  )
  message(FATAL_ERROR "")
endif()

# Useful for python script to work later:
set(ENV{PYTHONPATH} "${CMAKE_SOURCE_DIR}/python")

# Configure the run_setup_py.cmake.in script,
# and have it run at installation:

# We will pass the DEB_PACAKGE flag in debian/rules,
# because python packages on debian need special flags
if(DEB_PACKAGE)
  set(SETUP_PY_ARGS "--install-layout=deb" "--no-compile")
endif()

list(APPEND SETUP_PY_ARGS "--prefix=${CMAKE_INSTALL_PREFIX}")

configure_file(
  "${CMAKE_SOURCE_DIR}/run_setup_py.cmake.in"
  "${CMAKE_BINARY_DIR}/run_setup_py.cmake"
  @ONLY)

install(SCRIPT "${CMAKE_BINARY_DIR}/run_setup_py.cmake")


if(NOT WITH_DOCS)
  return()
endif()

# Generate man pages with rst2man (part of docutils)
find_program(_rst2man NAMES rst2man rst2man.py)
if(NOT _rst2man)
  message(STATUS "Please install docutils to generate man pages")
  return()
endif()

file(GLOB _man_srcs ${CMAKE_SOURCE_DIR}/doc/source/man/*.rst)
set(_man_out "${CMAKE_BINARY_DIR}/man1")
file(MAKE_DIRECTORY ${_man_out})
set(_commands)
foreach(_man_rst ${_man_srcs})
  get_filename_component(_name ${_man_rst} NAME_WE)
  list(APPEND _commands
    COMMAND ${_rst2man} "${_man_rst}" "${_man_out}/${_name}.1"
  )
endforeach()
add_custom_target(man ALL ${_commands})
install(
  DIRECTORY    ${CMAKE_BINARY_DIR}/man1
  DESTINATION  ${CMAKE_INSTALL_PREFIX}/share/man/
)
