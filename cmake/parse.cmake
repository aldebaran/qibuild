##
## parse.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Sat Oct 10 21:15:18 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Cedric GESTES
##

#regroup argument parsing functions



############################
# Extract one options from args
# result contain the list of args
# _option is the option to parse
# _is_available is true if the option is available
############################
function(parse_is_options _result _option _is_available)
  set(${_is_available} 0 PARENT_SCOPE)

  if (NOT ARGN)
    return()
  endif()

  #debug("PARSE: isopt: ${ARGN}")

  foreach(_arg ${ARGN})
    if ("${_arg}" STREQUAL "${_option}")
      set(${_is_available} 1 PARENT_SCOPE)
    endif ("${_arg}" STREQUAL "${_option}")
  endforeach(_arg ${ARGN})

  #remove the option from the list
  set(_tagada ${ARGN})
  list(REMOVE_ITEM _tagada "${_option}")
  set(${_result} ${_tagada} PARENT_SCOPE)
endfunction(parse_is_options)

###########################
# parse complicated argument
# get all args after _name before something in _keywords
#
# eg: extract all file undex SRC and HEADER when call with:
#     subargs_parse_arags("SRC" "SRC;MOC" _src_args _other_args SRC myfile.c myfile2.c HEADER myhead.h myhead2 blabla)
#     will return :
#      _src_args    = myfile.c myfile2.c
#      _other_args  = HEADER myhead.h myhead2 blabla
###########################
function(subargs_parse_args _name _keywords _args _defargs)
  set(_defresult       "" PARENT_SCOPE)
  set(_result          "" PARENT_SCOPE)
  set(please_get_me FALSE)

  foreach(_aarg ${ARGN})
    #search for keywords
    foreach(i ${_keywords})
      if (${i} STREQUAL "${_aarg}")
        #keywork found
        set(please_get_me FALSE)
      endif (${i} STREQUAL "${_aarg}")
    endforeach(i in ${_keywords})

    if (please_get_me)
      #append to result
      set(_result ${_result} ${_aarg})
    else (please_get_me)
#       message(STATUS "thr ${_aarg} = ${_name}")

      if (_name STREQUAL _aarg)
        #start appending to result
        set(please_get_me TRUE)
#         message(STATUS "there ${_aarg} = ${_name}")
      else (_name STREQUAL _aarg)

        #append to default result
        set(_defresult ${_defresult} ${_aarg})
      endif (_name STREQUAL _aarg)

    endif (please_get_me)
  endforeach(_aarg ${ARGN})

  set(${_args}          ${_result}    PARENT_SCOPE)
  set(${_defargs}       ${_defresult} PARENT_SCOPE)
#   debug("subargs: ${_name}, ${ARGN}")
#   debug("subargs: args: ${_result}")
#   debug("subargs: args: ${_defresult}")
endfunction(subargs_parse_args)




###########################
#@param _pkg       : return the package to process
#@param _plateform : return true if the pkg is needed for the current plateform
#@param _optional  : return true if the package is optional
#
#
# if no REQUIRED/OPTIONAL or PLATEFORM is specified in argument, the previous one still apply
###########################
function(use_lib_parse_options _pkg _nargs _plateform _optional)

  set(_pkg "" PARENT_SCOPE)

  #set the current plateform
  set(_cplateform "")
  set(_setplateform 0)

  #previous args (returned as _args for the next call)
  set(_pargs ${ARGN})

  foreach(_p ${ARGN})
    #remove the first item of _pargs
    list(REMOVE_AT _pargs 0)
    #MESSAGE(STATUS "_pargs is : ${_pargs}")

    if    (_p STREQUAL "REQUIRED")
      set(_optional 0 PARENT_SCOPE)
    elseif(_p STREQUAL "OPTIONAL")
      set(_optional 1 PARENT_SCOPE)

    elseif(_p STREQUAL "WINDOWS")
      set(_setplateform 1)
      set(_cplateform "${_cplateform};windows")
    elseif(_p STREQUAL "MACOSX")
      set(_setplateform 1)
      set(_cplateform "${_cplateform};macosx")
    elseif(_p STREQUAL "LINUX")
      set(_setplateform 1)
      set(_cplateform "${_cplateform};linux")
    elseif(_p STREQUAL "ALL")
      set(_setplateform 1)
      set(_cplateform "")

    else  (_p STREQUAL "REQUIRED")
      set(_pkg "${_p}" PARENT_SCOPE)
      break()
    endif (_p STREQUAL "REQUIRED")

  endforeach(_p ${ARGN})

  #plateform modified => see if the current plateform match one in _cplateform
  if (_setplateform)
    set(_plateform 0 PARENT_SCOPE)
    if (NOT _cplateform STREQUAL "")
      foreach(_plate ${_cplateform})
        #for example we match linux and linux64 as the same plateform
        if (TARGET_ARCH MATCHES "${_plate}.*")
          set(_plateform 1 PARENT_SCOPE)
          break()
        endif ()
      endforeach(_plate ${_cplateform})
    endif (NOT _cplateform STREQUAL "")

    #plateform is ok when Empty or ALL
    if (_cplateform STREQUAL "")
      set(_plateform 1 PARENT_SCOPE)
    endif(_cplateform STREQUAL "")
  endif (_setplateform)

  set(_nargs ${_pargs} PARENT_SCOPE)

endfunction(use_lib_parse_options)



#parse a SUBFOLDER argument
#
#  subfolder_parse_args(_subfolder _args ${ARGN})
#
function(subfolder_parse_args _subfolder _args)
  parse_option_with_arg("SUBFOLDER" _retoption _retargs ${ARGN})
  set(${_subfolder}  ${_retoption}    PARENT_SCOPE)
  set(${_args}       ${_retargs}      PARENT_SCOPE)
endfunction(subfolder_parse_args)

#############
# parse_option_with_arg("SUBFOLDER" _the_subfolder _args ${ARGN})
#############
function(parse_option_with_arg _option _result _args)
  set(${_result}       "" PARENT_SCOPE)
  set(_ret             "")
  set(please_get_me FALSE)

  foreach(_arg ${ARGN})
    if (please_get_me)
      set(${_result} ${_arg} PARENT_SCOPE)
      set(please_get_me FALSE)
    elseif (_arg STREQUAL ${_option})
      set(please_get_me TRUE)
    else (_arg STREQUAL ${_option})
      set(_ret ${_ret} ${_arg})
    endif (please_get_me)
  endforeach(_arg ${ARGN})
  set(${_args}       ${_ret} PARENT_SCOPE)
endfunction()
