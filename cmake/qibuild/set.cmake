##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

macro(qi_set_global name value)
  set("${name}" ${value} CACHE INTERNAL "" FORCE)
endmacro()
