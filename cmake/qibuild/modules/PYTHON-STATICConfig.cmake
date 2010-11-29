## Copyright (C) 2008 Aldebaran Robotics


if(NOT ${SDK_ARCH} STREQUAL "linux")
  message(FATAL_ERROR "This hack is for linux only")
else()
  clean(PYTHON-STATIC)
  fpath(PYTHON-STATIC Python.h PATH_SUFFIXES "python2.6")
  flib(PYTHON-STATIC python2.6-static PATH_SUFFIXES "python2.6")
  export_lib(PYTHON-STATIC)
endif()
