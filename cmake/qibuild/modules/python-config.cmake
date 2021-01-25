## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PYTHON)
# first, use fpath flib to get python from one of our pre-compiled packages
# note than we patch Python.h to NOT autolink with python27_d.lib,
# which prevent us from using boost_python
fpath(PYTHON Python.h PATH_SUFFIXES "python2.7")
flib(PYTHON NAMES python27 python2.7 Python)
set(_python_deps)
if(UNIX)
  list(APPEND _python_deps PTHREAD)
  if(APPLE)
  else()
    # linux
    list(APPEND _python_deps DL UTIL)
  endif()
endif()

qi_persistent_set(PYTHON_DEPENDS ${_python_deps})

if(NOT PYTHON_LIBRARIES OR NOT PYTHON_INCLUDE_DIRS)
  # If it does not work, use upstream cmake code
  # Note: upstream code does NOT work with visual studio on debug
  clean(PYTHON)
  unset(PYTHON_INCLUDE_DIRS)
  unset(PYTHON_INCLUDE_DIRS CACHE)
  find_package(PythonLibs 2)
  if(PYTHONLIBS_FOUND)
    qi_persistent_set(PYTHON_PACKAGE_FOUND FALSE)
  else()
    qi_persistent_set(PYTHON_LIBRARIES ${PYTHON_LIBRARY})
    qi_persistent_set(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR})
  endif()
endif()
export_lib(PYTHON)

