##
## Arguments example
##

#define a function with two required arguments, and many optionnal arguments
function(myfunctionwitharguments _positional_arg1 _positional_arg2)
  qi_argn_init(${ARGN})
  qi_argn_flags(SHARED STATIC)
  qi_argn_params(NAME DESC OUTPUTNAME)
  qi_argn_groups(SRC DEPS)

  message(STATUS "arg1: ${_positional_arg1}")
  message(STATUS "arg2: ${_positional_arg1}")

  message(STATUS "Is shared: ${argn_flag_is_shared}")
  message(STATUS "Is static: ${argn_flag_is_static}")

  message(STATUS "Name: ${argn_param_name}")
  message(STATUS "Desc: ${argn_param_desc}")

  message(STATUS "SRC:  ${argn_group_src}")
  message(STATUS "DEPS: ${argn_group_deps}")

endfunction()

myfunctionwitharguments("superarg1" "supraarg2")

myfunctionwitharguments("superarg1" "supraarg2" NAME "bing")

myfunctionwitharguments("superarg1" "supraarg2" NAME "bing" SRC "bing.h" "bing.c" DEPS "windows" "linux" DESC "a super function")
