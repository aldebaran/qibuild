##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

# on linux, it is advised to use openvc
# from system.
# (this way you get gtk bindings ...)

# otherwise, we'll use openv from toolchain-pc.

# Please not, however that you should install
# opencv by hand to get peopledection example
# working
if (${SDK_ARCH} STREQUAL "linux")
  set(_in_system "SYSTEM")
endif()


clean(OPENCV)
fpath(OPENCV opencv/cv.h ${_in_system} )
flib(OPENCV OPTIMIZED NAMES cv      cv200       ${_in_system})
flib(OPENCV DEBUG     NAMES cv      cv200d      ${_in_system})
flib(OPENCV OPTIMIZED NAMES cvaux   cvaux200    ${_in_system})
flib(OPENCV DEBUG     NAMES cvaux   cvaux200d   ${_in_system})
flib(OPENCV OPTIMIZED NAMES cxcore  cxcore200   ${_in_system})
flib(OPENCV DEBUG     NAMES cxcore  cxcore200d  ${_in_system})
flib(OPENCV OPTIMIZED NAMES highgui highgui200  ${_in_system})
flib(OPENCV DEBUG     NAMES highgui highgui200d ${_in_system})
flib(OPENCV OPTIMIZED NAMES ml      ml200d      ${_in_system})
flib(OPENCV DEBUG     NAMES ml      ml200       ${_in_system})
export_lib(OPENCV)
