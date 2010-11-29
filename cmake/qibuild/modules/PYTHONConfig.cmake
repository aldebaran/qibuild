## Copyright (C) 2008, 2010 Aldebaran Robotics

clean(PYTHON)

fpath(PYTHON Python.h PATH_SUFFIXES "python2.7" "python2.6")
flib(PYTHON OPTIMIZED NAMES python27 python2.7
                            python26 python2.6
                            Python)
flib(PYTHON DEBUG     NAMES python27_d python2.7
                            python26_d python2.6
                            Python)
export_lib(PYTHON)
