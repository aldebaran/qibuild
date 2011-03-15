##
## Copyright (C) 2010 Aldebaran Robotics
##

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the T001CHAIN project  #
###############################################

set(BOOTSTRAP_VERSION 4)

# Function to use qibuild from a old toc project
function(use_qibuild)
  if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)
    include(${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)

    set(NO_WARN_DEPRECATED TRUE PARENT_SCOPE)
    include(qibuild/compat/compat)
  endif()
endfunction()

if (CMAKE_TOOLCHAIN_FILE)
  # a toolchain which defines TOOLCHAIN_DIR -> toc
  if(TOOLCHAIN_DIR)
    # toc --cross -> qibuild (ctc uses qibuild now)
    if(OE_CROSS_DIR)
      use_qibuild()
      return()
    else()
      set(T001CHAIN_DIR ${TOOLCHAIN_DIR} CACHE PATH "" FORCE)
      include("${T001CHAIN_DIR}/cmake/general.cmake")
      return()
    endif()
  endif()
endif()

use_qibuild()
