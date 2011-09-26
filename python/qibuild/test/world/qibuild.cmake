## Copyright (C) 2011 Aldebaran Robotics

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the qibuild project    #
###############################################

set(QIBUILD_BOOTSTRAP_VERSION 10)

if(EXISTS ${CMAKE_BINARY_DIR}/dependencies.cmake)
  include(${CMAKE_BINARY_DIR}/dependencies.cmake)
endif()

include(qibuild/general
  OPTIONAL
  RESULT_VARIABLE _qibuild_found)

if(NOT _qibuild_found)
  message(FATAL_ERROR "
Could not find the qibuild CMake framework
    include(qibuild/general)
did not work
If you are using qibuild command line tool, please check your installation
If you are cross-compiling, make sure you are using a correct toolchain.cmake file.
")

endif()
