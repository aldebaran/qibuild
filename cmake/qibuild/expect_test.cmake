##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

function(_test_expect_bootstrap)
  message(STATUS "Bootstraping test")
  qi_expect_true(TRUE)
  if (${_expect} EQUAL FALSE)
    qi_error("TRUE is FALSE")
  endif()

  qi_expect_true(${_expect})
  if (${_expect} EQUAL FALSE)
    qi_error("_expect is false")
  endif()

  qi_expect_false(FALSE)
  if (${_expect} EQUAL TRUE)
    qi_error("TRUE is FALSE")
  endif()

  message(STATUS "Should FAIL")
  qi_expect_false(TRUE)
  qi_expect_false(${_expect})
  if (${_expect} EQUAL FALSE)
    qi_error("_expect is false")
  endif()
  message(STATUS "")
endfunction()


function(_test_expect_true)
  message(STATUS "Testing expect_true")
  qi_expect_true(TRUE)
  qi_expect_true(${_expect})

  qi_expect_true(ON)
  qi_expect_true(${_expect})

  set(paf TRUE)
  qi_expect_true(paf)
  qi_expect_true(${_expect})

  set(paf TRUE)
  qi_expect_true(${paf})
  qi_expect_true(${_expect})

  set(paf TRUE)
  qi_expect_true("${paf}")
  qi_expect_true(${_expect})

  set(paf FALSE)
  #this is weird but this will test
  message(STATUS "Should FAIL")
  qi_expect_true(paf)
  qi_expect_false(${_expect})

  set(paf FALSE)
  message(STATUS "Should FAIL")
  qi_expect_true(${paf})
  qi_expect_false(${_expect})

  set(paf FALSE)
  message(STATUS "Should FAIL")
  qi_expect_true("${paf}")
  qi_expect_false(${_expect})

  message(STATUS "")
endfunction()

function(_test_expect_false)
  message(STATUS "Testing expect_false")
  qi_expect_false(FALSE)
  qi_expect_true(${_expect})

  qi_expect_false(OFF)
  qi_expect_true(${_expect})

  set(paf FALSE)
  qi_expect_false(paf)
  qi_expect_true(${_expect})

  set(paf FALSE)
  qi_expect_false(${paf})
  qi_expect_true(${_expect})

  set(paf FALSE)
  qi_expect_false("${paf}")
  qi_expect_true(${_expect})

  qi_expect_false(BIM)
  qi_expect_true(${_expect})

  set(paf TRUEBUT)
  qi_expect_false(paf)
  qi_expect_true(${_expect})

  set(paf TRUEBUT)
  qi_expect_false(${paf})
  qi_expect_true(${_expect})

  set(paf TRUEBUT)
  qi_expect_false("${paf}")
  qi_expect_true(${_expect})

  message(STATUS "")
endfunction()

function(_test_expect_bool)
  message(STATUS "Testing expect_bool")

  _qi_expect_bool("NOVAR" "TRUE")
  qi_expect_true(${_expect})

  _qi_expect_bool("NOVAR" "FALSE")
  qi_expect_true(${_expect})

  _qi_expect_bool("NOVAR" "TrUe")
  qi_expect_true(${_expect})

  _qi_expect_bool("NOVAR" "ThisIsNotBool")
  qi_expect_false(${_expect})

  _qi_expect_bool("NOVAR" "Youki")
  qi_expect_false(${_expect})

  set(MyVar "totot")
  _qi_expect_bool("MyVar" "totot")
  qi_expect_false(${_expect})

  _qi_expect_bool("MyVar" "N")
  qi_expect_true(${_expect})

  _qi_expect_bool("MyVar" N)
  qi_expect_true(${_expect})

  set(MyVar "totot")
  _qi_expect_bool("MyVar" "MyVar-NOTFOUND")
  qi_expect_true(${_expect})

  message(STATUS "")
endfunction(_test_expect_bool)


function(_test_expect_strequal)
  message(STATUS "Testing expect_strequal")

  message(STATUS "Should FAIL")
  qi_expect_strequal("TOTO" "TITI")
  qi_expect_false(${_expect})

  qi_expect_strequal("TOTO" "TOTO")
  qi_expect_true(${_expect})

  qi_expect_strequal("TOTO TUTU" "TOTO TUTU")
  qi_expect_true(${_expect})

  message(STATUS "Should FAIL")
  qi_expect_strequal("TOTO" "ToTo")
  qi_expect_false(${_expect})

  message(STATUS "Should FAIL")
  qi_expect_strequal(TOTO ToTo)
  qi_expect_false(${_expect})

  set(myvar "ToTo")
  message(STATUS "Should FAIL")
  qi_expect_strequal(myvar TOTO)
  qi_expect_false(${_expect})

  set(myvar "TOTO")
  qi_expect_strequal(myvar TOTO)
  qi_expect_true(${_expect})

  set(myvar "TOTO")
  message(STATUS "Should FAIL")
  qi_expect_strequal(${myvar} ToTo)
  qi_expect_false(${_expect})

  message(STATUS "")
endfunction()


_test_expect_bootstrap()
_test_expect_true()
_test_expect_false()
_test_expect_bool()
_test_expect_strequal()
