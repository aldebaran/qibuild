##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

# expect_true and expect_false dereference variable so CMP0012 must be set.

# if() recognizes numbers and boolean constants.
cmake_policy(SET CMP0012 NEW)

# Bad variable reference syntax is an error.
cmake_policy(SET CMP0010 NEW)

function(_qi_expect_bool _var_name _bool_value)

  # True if the constant is 1, ON, YES, TRUE, Y, or a non-zero number.
  # False if the constant is 0, OFF, NO, FALSE, N, IGNORE, "", or ends in the suffix '-NOTFOUND'.
  # Named boolean constants are case-insensitive.
  set(_expect TRUE PARENT_SCOPE)
  if ("${_bool_value}" STREQUAL "")
    #message(STATUS "Empty")
    return()
  endif()

  string(TOUPPER "${_bool_value}" _upper_bool_value)

  if ("${_upper_bool_value}" MATCHES "^(ON|YES|TRUE|Y|OFF|NO|FALSE|N|IGNORE)$")
    #message(STATUS "Constant")
    return()
  endif()

  if ("${_bool_value}" MATCHES "^[0-9]*$")
    #message(STATUS "Number")
    return()
  endif()

  if ("${_bool_value}" MATCHES "^${_var_name}-NOTFOUND$")
    return()
  endif()

  set(_expect FALSE PARENT_SCOPE)
  message(STATUS "This variable is not a boolean: (${_var_name}:${_bool_value})")

endfunction()

function(qi_expect_false)
  set(_false_expr ${ARGN})

  if(DEFINED "${_false_expr}")
    _qi_expect_bool("${_false_expr}" "${${_false_expr}}")

    if (${${_false_expr}})
      message(STATUS "EXPECT FAIL -- V(${_false_expr}:${${_false_expr}}) is not False")
      set(_expect FALSE PARENT_SCOPE)
    else()
      message(STATUS "Expect Ok   -- V(${_false_expr}:${${_false_expr}}) is False")
      set(_expect TRUE PARENT_SCOPE)
    endif()
    return()
  endif()

  _qi_expect_bool("NO_VARIABLE" "${_false_expr}")
  if (${_false_expr})
    message(STATUS "EXPECT FAIL -- (${_false_expr}) is not FALSE")
    set(_expect FALSE PARENT_SCOPE)
  else()
    message(STATUS "Expect Ok   -- (${_false_expr}) is FALSE")
    set(_expect TRUE PARENT_SCOPE)
  endif()


endfunction()




function(qi_expect_true _true_expr)

  if(DEFINED "${_true_expr}")
    #this is a variable
    _qi_expect_bool("${_true_expr}" "${${_true_expr}}")
    if (${${_true_expr}})
      message(STATUS "Expect Ok   -- V(${_true_expr}:${${_true_expr}}) is True")
      set(_expect TRUE PARENT_SCOPE)
    else()
      message(STATUS "EXPECT FAIL -- V(${_true_expr}:${${_true_expr}}) is not True")
      set(_expect FALSE PARENT_SCOPE)
    endif()
    return()
  endif()

  _qi_expect_bool("NO_VARIABLE" "${_true_expr}")
  if (${_true_expr})
    message(STATUS "Expect Ok   -- (${_true_expr}) is True")
    set(_expect TRUE PARENT_SCOPE)
  else()
    message(STATUS "EXPECT FAIL -- (${_true_expr}) is not True")
    set(_expect FALSE PARENT_SCOPE)
  endif()

endfunction()

function(qi_expect_strequal _string1 _string2)
  set(_mystring1 "${_string1}")
  set(_mystring2 "${_string2}")
  if (DEFINED "${_string1}")
    set(_var1 "${_string1}")
    set(_mystring1 "${${_string1}}")
  endif()
  if (DEFINED "${_string2}")
    set(_var2 "${_string2}")
    set(_mystring2 "${${_string2}}")
  endif()

  if ("${_mystring1}" STREQUAL "${_mystring2}")
    message(STATUS "Expect Ok   -- (${_var1}:${_mystring1}) is equal to (${_var2}:${_mystring2})")
    set(_expect TRUE PARENT_SCOPE)
  else()
    message(STATUS "EXPECT FAIL -- (${_var1}:${_mystring1}) is not equal to (${_var2}:${_mystring2})")
    set(_expect FALSE PARENT_SCOPE)
  endif()
endfunction()
