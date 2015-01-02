## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
message(STATUS "Running @_compiler@ @_in@ @_out@")
execute_process(COMMAND "@_compiler@" "@_in@" "@_out@"
  OUTPUT_VARIABLE _compile_out
  ERROR_VARIABLE _compile_err
  RESULT_VARIABLE _compile_ret)


if(NOT ${_compile_ret} EQUAL 0)
  message(FATAL_ERROR "Compilation failed. (retcode: ${_compile_ret})
out: ${_compile_out}
err: ${_compile_err}
")
endif()
