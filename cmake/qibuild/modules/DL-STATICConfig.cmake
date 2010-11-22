##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

clean(DL-STATIC)
fpath(DL-STATIC dlfcn.h SYSTEM)
flib(DL-STATIC dl SYSTEM)
export_lib(DL-STATIC)
