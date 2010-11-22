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

clean(URG)

fpath(URG "urg_ctrl.h" PATH_SUFFIXES "urg")
flib(URG "c_connection")
flib(URG "c_urg")
flib(URG "c_system")

export_lib(URG)
