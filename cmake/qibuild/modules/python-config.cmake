## Copyright (C) 2011 Aldebaran Robotics

clean(PYTHON)
if (WIN32 AND NOT MSVC)
  # On mingw it's very easy: the python library and headers are
  # installed next to the executable.
  find_program(_python NAMES python)
  if(NOT _python)
    qi_error("Could not find python!")
  endif()

  get_filename_component(_python_path ${_python} PATH)
  fpath(PYTHON Python.h "${_python_path}/include")
  flib(PYTHON  python26 python27 "${_python_path}/libs")
else()
  # Other platforms: libraries could come from a pre-compiled package,
  # so never use the python executable
  fpath(PYTHON Python.h PATH_SUFFIXES "python2.7" "python2.6")
  flib(PYTHON OPTIMIZED NAMES python27 python2.7
                              python26 python2.6
                              Python)
  flib(PYTHON DEBUG     NAMES python27_d python2.7
                              python26_d python2.6
                              Python)
endif()
export_lib(PYTHON)

