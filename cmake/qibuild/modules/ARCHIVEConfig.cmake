##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

#get the root folder of this sdk
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
set(TOOLCHAIN_PC_ROOT ${_ROOT_DIR}/../../)

clean(ARCHIVE)
fpath(ARCHIVE archive.h PATH_SUFFIXES archive)

if(WIN32)
  flib(ARCHIVE OPTIMIZED NAMES archive)
  flib(ARCHIVE DEBUG     NAMES archive_d)
else()
  flib(ARCHIVE NAMES archive)
endif()

if (TARGET_HOST STREQUAL "TARGET_HOST_MACOSX")
  depend(ARCHIVE REQUIRED ZLIB)
endif (TARGET_HOST STREQUAL "TARGET_HOST_MACOSX")

export_lib(ARCHIVE)

