##
## Copyright (C) 2010 Aldebaran Robotics
##

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the qibuild project    #
###############################################

set(QIBUILD_BOOTSTRAP_VERSION 1)

find_program(QI_BUILD qibuild)
if(NOT QI_BUILD)
  message(STATUS
    "
    Could not find qibuild executable.

    Please check your setup.

    "
  )
  message(FATAL_ERROR "")
endif()


##
# Create a use_qibuild.cmake file in CMAKE_BINARY_DIR,
# and include it.
# This allow us to find all qibuild/qibuild.cmake
function(bootstrap)
  execute_process(
      COMMAND ${QI_BUILD} bootstrap ${CMAKE_BINARY_DIR}
      RESULT_VARIABLE  _retcode
      OUTPUT_VARIABLE  _stdout
      ERROR_VARIABLE   _stderr
      )
  if(NOT ${_retcode} EQUAL 0)
    message(STATUS
        "
        qibuild bootstrap fail!
        Log:
        ====
        ${QI_BUILD} bootstrap ${CMAKE_BINARY_DIR}
        ${_stdout}
        ${_stderr}

        ===

        Please file a bug report with a comple CMake log
        "
    )
      message(FATAL_ERROR "")
  endif()
endfunction()

if(NOT EXISTS ${CMAKE_BINARY_DIR}/use_qibuild.cmake)
  bootstrap()
endif()

include(${CMAKE_BINARY_DIR}/use_qibuild.cmake)

# If we used `qibuild configure`, a find_deps.cmake file
# has been generated in CMAKE_BINARY_DIR to find the
# dependencies.
if(EXISTS ${CMAKE_BINARY_DIR}/find_deps.cmake)
  include(${CMAKE_BINARY_DIR}/find_deps.cmake)
endif()
