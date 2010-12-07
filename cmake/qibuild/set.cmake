##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

macro(qi_set_global name)
  set("${name}" ${ARGN} CACHE INTERNAL "" FORCE)
endmacro()

macro(qi_set_cache name)
  set("${name}" ${ARGN} CACHE STRING "" FORCE)
endmacro()

macro(qi_set_advanced_cache name)
  set("${name}" ${ARGN} CACHE STRING "" FORCE)
  mark_as_advanced("${name}")
endmacro()
