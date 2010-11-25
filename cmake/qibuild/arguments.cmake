##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

#! QiBuild Arguments
# ==================
# Cedric GESTES <gestes@aldebaran-robotics.com>

#!
# This modules ease the parsing of arguments.
# Arguments are splitted by types, there could be:
#
# * args: positionnal arguments
# * flags: boolean value, the flags could be present or not (IS_OPEN?)
# * params: simple optional parameter
# * groups: list of optional arguments
#
#


#!
# Init parsing
# most of the time you only want to call this function with ${ARGN} of the calling function.
# This function must always be called once before other qi_argn_ functions.
#
# \argn: parameters parsed by later call to qi_argn_ functions.
# \example:arguments
function(qi_argn_init)
  set(argn_init TRUE PARENT_SCOPE)
  set(argn_remaining ${ARGN} PARENT_SCOPE)
endfunction()

#!
# parse flags.
# For each flags a variable of the form 'argn_flags_<paramname>' (all in lower case) will be set in the parent scope.
# Remaining args will be in argn_remaining.
#
# WARNING: must be called before qi_argn_groups and qi_argn_params
#
# \argn: flags list
function(qi_argn_flags)
  if (NOT argn_init)
    qi_error("You should not call qi_argn_init before calling qi_argn_flags")
  endif()

  if (argn_params_processed)
    qi_error("You should not call qi_argn_flags after qi_argn_params")
  endif()

  if (argn_groups_processed)
    qi_error("You should not call qi_argn_flags after qi_argn_groups")
  endif()

  set(argn_flags_processed TRUE PARENT_SCOPE)

  #store the remaining arguments list
  set(_temp_list ${argn_remaining})
  #message(STATUS "Argument list is: ${_temp_list}")

  foreach(_flag ${ARGN})
    #set the output name
    string(TOLOWER "argn_flag_${_flag}" _PARENT_flag)
    #clear the parent variable
    #message("${_PARENT_flag}=")
    set(${_PARENT_flag} FALSE PARENT_SCOPE)

    #message(STATUS "Searching for '${_flag}'")
    foreach(_arg ${argn_remaining})
      if ("${_arg}" STREQUAL "${_flag}")
        #message(STATUS "Matched: '${_flag}'")
        #message("${_PARENT_flag}=${_flag}")
        set(${_PARENT_flag} TRUE PARENT_SCOPE)
        list(REMOVE_ITEM _temp_list "${_flag}")
      endif ()
    endforeach()
  endforeach()
  #message(STATUS "Return list is: ${_temp_list}")
  set(argn_remaining ${_temp_list} PARENT_SCOPE)

endfunction()


#!
# parse single optional parameters.
# For each parameters a variable of the form 'argn_params_<paramname>' (all in lower case) will be set in the parent scope.
# remaining args will be in argn_remaining.
# WARNING: must be called before qi_argn_groups
#
# \argn: parameters list
function(qi_argn_params)
  if (NOT argn_init)
    qi_error("You should not call qi_argn_init before calling qi_argn_params")
  endif()

  set(argn_params_processed TRUE PARENT_SCOPE)

  if (argn_groups_processed)
    qi_error("You should not call qi_argn_params after qi_argn_groups")
  endif()

  #store the remaining arguments list
  set(_my_argn_remaining ${argn_remaining})

  foreach(_param ${ARGN})
    #set the output name
    string(TOLOWER "argn_param_${_param}" _PARENT_flag)
    #clear the parent variable
    set(${_PARENT_flag} PARENT_SCOPE)

    set(_temp_list)
    set(please_get_me_done FALSE)
    set(please_get_me FALSE)
    foreach(_arg ${_my_argn_remaining})
      #eat a param
      if (please_get_me)
        set(${_PARENT_flag} "${_arg}" PARENT_SCOPE)
        set(please_get_me      FALSE)
        #do not eat further arg for this param
        set(please_get_me_done TRUE)
      else()
        if (NOT please_get_me_done AND "${_arg}" STREQUAL "${_param}")
          #eat the next item
          set(please_get_me TRUE)
        else()
          set(_temp_list ${_temp_list} ${_arg})
        endif ()
      endif()
    endforeach()
    set(_my_argn_remaining ${_temp_list})
  endforeach()

  set(argn_remaining ${_my_argn_remaining} PARENT_SCOPE)
endfunction()

#!
# parse groups of arguments.
# For each groups a variable of the form 'argn_groups_<paramname>' (all in lower case) will be set in the parent scope.
# remaining args will be in argn_remaining.
#
# \argn: groups list
function(qi_argn_groups)
  if (NOT argn_init)
    qi_error("You should not call qi_argn_init before calling qi_argn_groups")
  endif()

  set(argn_groups_processed TRUE PARENT_SCOPE)
  #TODO: check that qi_arg_groups has not been called

  #store the remaining arguments list
  set(_my_argn_remaining ${argn_remaining})

  foreach(_param ${ARGN})

    #set the output name
    string(TOLOWER "argn_group_${_param}" _PARENT_flag)
    #clear the parent variable
    set(${_PARENT_flag} PARENT_SCOPE)

    set(_temp_list)
    set(please_get_me_done)
    set(please_get_me)
    set(_temp_value)

    foreach(_arg ${_my_argn_remaining})

      #search for a delimiter
      foreach(_param2 ${ARGN})
        if ("${_param2}" STREQUAL "${_arg}")
          set(please_get_me)
        endif()
      endforeach()

      #eat a param
      if (please_get_me)
        set(_temp_value ${_temp_value} ${_arg})
      else()
        if (NOT please_get_me_done AND "${_arg}" STREQUAL "${_param}")
          #eat the next item
          set(please_get_me TRUE)
        else()
          set(_temp_list ${_temp_list} ${_arg})
        endif ()
      endif()
    endforeach()

    #store the value in the parent scope
    set(${_PARENT_flag} "${_temp_value}" PARENT_SCOPE)

    set(_my_argn_remaining ${_temp_list})
  endforeach()

  set(argn_remaining ${_my_argn_remaining} PARENT_SCOPE)
endfunction()
