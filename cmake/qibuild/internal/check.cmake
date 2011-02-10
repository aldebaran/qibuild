## Copyright (C) 2011 Aldebaran Robotics

function(check_is_target _name)
  if (NOT TARGET ${_name})
    error("[${_name}] is not a target verify your function arguments")
  endif()
endfunction()

