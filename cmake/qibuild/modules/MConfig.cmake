##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(M)
fpath(M "math.h" SYSTEM)
flib(M "m" SYSTEM)
export_lib(M)
