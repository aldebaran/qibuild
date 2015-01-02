## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PYTHON3)


#do not include python3 this is not the real python library.
set(_pyt_version
  "python3.7m" "python3.7"
  "python3.6m" "python3.6"
  "python3.5m" "python3.5"
  "python3.4m" "python3.4"
  "python3.3m" "python3.3"
  "python3.2m" "python3.2"
  "python3.1m" "python3.1"
  "python3.0m" "python3.0"
)


fpath(PYTHON3 Python.h PATH_SUFFIXES ${_pyt_version})
flib(PYTHON3 NAMES ${_pyt_version})
set(_python_deps)
if(UNIX)
  list(APPEND _python_deps PTHREAD)
  if(APPLE)
  else()
    # linux
    list(APPEND _python_deps DL UTIL)
  endif()
endif()

qi_persistent_set(PYTHON3_DEPENDS ${_python_deps})

export_lib(PYTHON3)
