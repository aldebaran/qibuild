## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# You can use this CMake file to install qibuild on your
# system, if you want to, but please not that you
# won't be able to uninstall it afterward.
# It is advised you use the ./install-qibuild scripts instead, or the
# packages provided by Aldebaran

cmake_minimum_required(VERSION 2.8)

project(qiBuild NONE)

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

# Generate man pages with sphinx:
find_program(_sphinx_build sphinx-build)
if(NOT _sphinx_build)
  message(STATUS "Please install python-sphinx to generate "
  "documentation and man pages"
  )
else()
  execute_process(COMMAND
    ${_sphinx_build}
    "-b" "man"
    "${CMAKE_SOURCE_DIR}/doc"
    "${CMAKE_BINARY_DIR}/man1"
  )
  install(
    DIRECTORY    ${CMAKE_BINARY_DIR}/man1
    DESTINATION  ${CMAKE_INSTALL_PREFIX}/share/man/
    PATTERN      ".doctrees" EXCLUDE
  )
endif()


# Useful for python script to work later:
set(ENV{PYTHONPATH} "${CMAKE_SOURCE_DIR}/python")

# Generate and install manpages
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/doc)

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

if(_sphinx_build)
  add_custom_target("html-doc"
    ALL
      ${PYTHON_EXECUTABLE}
       "${CMAKE_SOURCE_DIR}/doc/tools/gen_cmake_doc.py"
       "${CMAKE_SOURCE_DIR}"
    COMMAND
      ${_sphinx_build}
      "-b" "html"
      ${CMAKE_SOURCE_DIR}/doc
      ${CMAKE_BINARY_DIR}/doc/html
  )
  install(
    DIRECTORY ${CMAKE_BINARY_DIR}/doc/html
    DESTINATION ${CMAKE_INSTALL_PREFIX}/share/qibuild/doc
    PATTERN      ".doctrees" EXCLUDE
  )
endif()

