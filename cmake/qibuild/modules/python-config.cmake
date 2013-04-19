## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PYTHON)
# first, use fpath flib to get python from one of our pre-compiled packages
# note than we patch Python.h to NOT autolink with python27_d.lib,
# which prevent us from using boost_python
fpath(PYTHON Python.h PATH_SUFFIXES "python2.7" "python2.6")
flib(PYTHON NAMES python27 python2.7 Python)

if(NOT PYTHON_LIBRARIES OR NOT PYTHON_INCLUDE_DIRS)
  # If it does not work, use upstream cmake code
  # Note: upstream code does NOT work with visual studio on debug
  clean(PYTHON)
  unset(PYTHON_INCLUDE_DIRS)
  unset(PYTHON_INCLUDE_DIRS CACHE)
  find_package(PythonLibs)
  if(PYTHONLIBS_FOUND)
    qi_set_global(PYTHON_PACKAGE_FOUND FALSE)
  else()
    qi_set_global(PYTHON_LIBRARIES ${PYTHON_LIBRARY})
    qi_set_global(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR})
  endif()
endif()
export_lib(PYTHON)

