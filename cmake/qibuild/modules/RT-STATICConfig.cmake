##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(RT-STATIC)
fpath(RT-STATIC time.h SYSTEM)
flib(RT-STATIC rt SYSTEM)
export_lib(RT-STATIC)
