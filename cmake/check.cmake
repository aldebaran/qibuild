##
## check.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Mon Oct 12 01:11:47 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Cedric GESTES
##


#WE REALLY DONT WANT TO BUILD IN THE SAME FOLDER AS SOURCE
#todo
#rif (NOT CMAKE_ALLOW_INSOURCE_BUILD)
if (${CMAKE_BINARY_DIR} STREQUAL ${CMAKE_CURRENT_SOURCE_DIR})
  message(STATUS
    "\n"
    "===========================================================\n"
    "= Do not run cmake in your source directory\n"
    "===========================================================\n"
    )
  message(FATAL_ERROR "\n")
  #TODO: be verbose
endif (${CMAKE_BINARY_DIR} STREQUAL ${CMAKE_CURRENT_SOURCE_DIR})

if (NOT SDK_ARCH)
  message(WARNING
    "\n"
    "===========================================================\n"
    "= SDK_ARCH is undefined                                   =\n"
    "= Set This variable in your toolchain.cmake file          =\n"
    "===========================================================\n"
    "")
  message(FATAL_ERROR "")
endif (NOT SDK_ARCH)

set(_supported_sdk_arch "win-vc8" "win-vc9" "linux" "linux64" "macosx" "nao-geode" "nao-atom")
set(_found)

foreach(_arch ${_supported_sdk_arch})

  if ("${_arch}" STREQUAL "${SDK_ARCH}")
    set(_found TRUE)
  endif ("${_arch}" STREQUAL "${SDK_ARCH}")

endforeach(_arch ${_supported_sdk_arch})

if (NOT _found)
  message(WARNING
    "\n"
    "===========================================================\n"
    "= SDK_ARCH is should be one of win-vc8, win-vc9, linux    =\n"
    "= macosx, nao-geode, nao-atom                             =\n"
    "===========================================================\n"
    "")
  message(FATAL_ERROR "")
endif (NOT _found)


# if (NOT SDK_EXTRA_DIRS)
#   message(WARNING
#     "\n"
#     "===========================================================\n"
#     "= SDK_EXTRA_DIRS not set. this is not fatal,              =\n"
#     "=  but this is mostly an unwanted situation               =\n"
#     "= Set this variable in your toolchain.cmake file          =\n"
#     "===========================================================\n"
#     "")
#   message(FATAL_ERROR "")
# endif (NOT SDK_EXTRA_DIRS)
