##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

function(_test_arguments_flags)
  message(STATUS "Testing qi_argn_flags")
  qi_argn_init(BOYS titi tutu GIRLS foo bar IS_CUTE)
  qi_argn_flags(IS_CUTE IS_CURRENT IS_OPEN)

  qi_expect_true(argn_flag_is_cute)
  qi_expect_true(${argn_flag_is_cute})
  qi_expect_true("${argn_flag_is_cute}")

  qi_expect_false(argn_flag_is_current)
  qi_expect_false(${argn_flag_is_current})
  qi_expect_false("${argn_flag_is_current}")
  qi_expect_strequal("${argn_remaining}" "BOYS;titi;tutu;GIRLS;foo;bar")
  message(STATUS "")
endfunction()


function(_test_arguments_params)
  message(STATUS "Testing qi_argn_params")
  qi_argn_init(NAME titi DESC "wistiti" BOYS titi tutu GIRLS foo bar IS_CUTE NAME bite)
  qi_argn_params(NAME DESC PAF)

  qi_expect_strequal("${argn_param_name}"    "titi")
  qi_expect_strequal("${argn_param_desc}"    "wistiti")
  qi_expect_strequal("${argn_param_paf}"     "")
  qi_expect_strequal("${argn_param_is_cute}" "")
  qi_expect_strequal("${argn_param_boys}"    "")
  qi_expect_strequal("${argn_param_girls}"   "")
  qi_expect_strequal("${argn_remaining}"     "BOYS;titi;tutu;GIRLS;foo;bar;IS_CUTE;NAME;bite")
  message(STATUS "")
endfunction()

function(_test_arguments_groups)
  message(STATUS "Testing qi_argn_groups")
  qi_argn_init(NAME titi DESC "wistiti" BOYS titi tutu GIRLS foo bar IS_CUTE NAME bite)
  qi_argn_groups(BOYS GIRLS SLIP)

  qi_expect_strequal("${argn_group_boys}"    "titi;tutu")
  qi_expect_strequal("${argn_group_girls}"   "foo;bar;IS_CUTE;NAME;bite")
  qi_expect_strequal("${argn_group_slip}"    "")
  qi_expect_strequal("${argn_group_is_cute}" "")
  qi_expect_strequal("${argn_group_name}"    "")
  qi_expect_strequal("${argn_group_desc}"    "")
  qi_expect_strequal("${argn_remaining}"     "NAME;titi;DESC;wistiti")
  message(STATUS "")
endfunction()

function(_test_arguments_all)
  message(STATUS "Testing qi_argn_all")
  qi_argn_init(NAME titi DESC "wistiti" BOYS titi tutu GIRLS foo bar IS_CUTE NAME bite)
  qi_argn_flags(IS_CUTE IS_OPEN IS_MEANINGFUL)
  qi_argn_params(NAME DESC CALOTTE)
  qi_argn_groups(BOYS GIRLS METRO)

  qi_expect_true(${argn_flag_is_cute})
  qi_expect_false(${argn_flag_is_open})
  qi_expect_false(${argn_flag_is_meaningfull})

  qi_expect_strequal("${argn_param_name}"    "titi")
  qi_expect_strequal("${argn_param_desc}"    "wistiti")
  qi_expect_strequal("${argn_param_calotte}" "")

  qi_expect_strequal("${argn_group_boys}"    "titi;tutu")
  qi_expect_strequal("${argn_group_girls}"   "foo;bar;NAME;bite")
  qi_expect_strequal("${argn_group_metro}"   "")

  qi_expect_strequal("${argn_remaining}"     "")
  message(STATUS "")
endfunction()


_test_arguments_flags()
_test_arguments_params()
_test_arguments_groups()
_test_arguments_all()
