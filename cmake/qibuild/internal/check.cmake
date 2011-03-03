## Copyright (C) 2011 Aldebaran Robotics

function(_qi_check_is_target _name)
  if (NOT TARGET ${_name})
    qi_error("[${_name}] is not a target verify your function arguments")
  endif()
endfunction()

