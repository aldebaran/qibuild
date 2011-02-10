## Copyright (C) 2011 Aldebaran Robotics



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
  set(ARCHIVE_DEPENDS "ZLIB")
endif()

export_lib(ARCHIVE)

