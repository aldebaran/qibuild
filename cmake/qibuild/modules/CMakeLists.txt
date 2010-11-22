##
## CMakeLists.txt
## Login : <ctaf@ctaf-maptop>
## Started on  Sat Sep 12 03:01:43 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

file(GLOB _cmakes RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}/" "*.cmake")
install_cmake("modules/" ${_cmakes})
