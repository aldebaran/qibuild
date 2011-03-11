##
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

# This CMakeLists is only here for packaging.
# Do not try to use for installing directly on you system:
#   * CMAKE_PREFIX_PATH is NOT used ! (so you will get
#       stuff on /usr instead of /usr/local)
#  * CMake does not handle un-install
#  Use the ./install-qibuild.sh script instead, or the
#  packages provided by Aldebaran

cmake_minimum_required(VERSION 2.6.4)

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
install(
  DIRECTORY
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/qibuild
  DESTINATION
    "share/cmake/modules"
)

# Useful for python script to work later:
set(ENV{PYTHONPATH} "${CMAKE_SOURCE_DIR}/python")

# Generate and install manpages
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/doc)
function(gen_man_pages)
  foreach(_name ${ARGN})
    execute_process(
      COMMAND
        ${PYTHON_EXECUTABLE}
        ${CMAKE_SOURCE_DIR}/doc/tools/generate_manpage_from_qibuild.py
        ${CMAKE_SOURCE_DIR}/doc/${_name}-manpage.txt
        ${CMAKE_BINARY_DIR}/doc/${_name}-manpage.txt
        "${_name}.actions"
      WORKING_DIRECTORY
        ${CMAKE_SOURCE_DIR}/python
    )

    execute_process(
     COMMAND
        a2x -f manpage ${CMAKE_BINARY_DIR}/doc/${_name}-manpage.txt
      WORKING_DIRECTORY
        ${CMAKE_BINARY_DIR}/doc
    )

    install(
    FILES
      ${CMAKE_BINARY_DIR}/doc/${_name}.1
    DESTINATION
      share/man/man1/
    )
  endforeach()
endfunction()

gen_man_pages(qisrc qibuild qitoolchain)


# Configure python/qibuild/config.py:
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/python/qibuild/config.py.in
  ${CMAKE_CURRENT_SOURCE_DIR}/python/qibuild/config.py
)

# Configure the run_setup_py.cmake.in script,
# and have it run at installation:


set(SETUP_PY_ARGS "--prefix=${CMAKE_INSTALL_PREFIX}")
# We will pass the DEB_PACAKGE flag in debian/rules,
# because python packages on debian need special flags
if(DEB_PACKAGE)
  list(APPEND SETUP_PY_ARGS "--install-layout=deb" "--no-compile")
endif()

configure_file(
  "${CMAKE_SOURCE_DIR}/run_setup_py.cmake.in"
  "${CMAKE_BINARY_DIR}/run_setup_py.cmake"
  @ONLY)

install(SCRIPT "${CMAKE_BINARY_DIR}/run_setup_py.cmake")

