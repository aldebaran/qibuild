##
## Copyright (C) 2010 Aldebaran Robotics
##

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the T001CHAIN project  #
###############################################

set(BOOTSTRAP_VERSION 3)

if (CMAKE_TOOLCHAIN_FILE)
  # a toolchain which defines TOOLCHAIN_DIR -> toc
  if(TOOLCHAIN_DIR)
    set(T001CHAIN_DIR ${TOOLCHAIN_DIR} CACHE PATH "" FORCE)
    include("${T001CHAIN_DIR}/cmake/general.cmake")
    return()
  endif()
endif()

# else, simply includes qibuild.cmake if it is there:
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)
  include(${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)

  # plus a few stuff:
  set(NO_WARN_DEPRECATED TRUE)
  include(qibuild/compat/compat)
endif()
