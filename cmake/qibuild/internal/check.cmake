##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

function(check_is_target _name)
  if (NOT TARGET ${_name})
    error("[${_name}] is not a target verify your function arguments")
  endif (NOT TARGET ${_name})
endfunction(check_is_target _name)

