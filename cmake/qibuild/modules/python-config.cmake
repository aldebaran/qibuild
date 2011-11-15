## Copyright (C) 2011 Aldebaran Robotics

clean(PYTHON)
# first, use fpath flib to get python from one of our pre-compiled packages
fpath(PYTHON Python.h PATH_SUFFIXES "python2.7" "python2.6")
flib(PYTHON OPTIMIZED NAMES python27 python2.7
                            python26 python2.6
                            Python)
flib(PYTHON DEBUG     NAMES python27_d python2.7
                              python26_d python2.6
                              Python)

if(NOT PYTHON_LIBRARIES OR NOT PYTHON_INCLUDE_DIRS)
  # If it does not work, use upstream cmake code
  # Note: upstream code does NOT work with visual studio on debug
  clean(PYTHON)
  unset(PYTHON_INCLUDE_DIRS)
  unset(PYTHON_INCLUDE_DIRS CACHE)
  find_package(PythonLibs REQUIRED)
  qi_set_global(PYTHON_LIBRARIES ${PYTHON_LIBRARY})
  qi_set_global(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR})
endif()
export_lib(PYTHON)

