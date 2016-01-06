## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Tools to run Python commands from CMake
# =========================================
#
# .. note:: we will make sure to always use Python2, which is
#           already a dependency of the ``qibuild`` command line
#
# If you are using the ``qibuild`` command line, you will be
# able to run python command that imports ``qibuild``

if (_QI_PYTHON_CMAKE)
  return()
endif()
set(_QI_PYTHON_CMAKE TRUE)


find_program(PYTHON2_EXECUTABLE NAMES python2 python NO_CMAKE_PATH)

function(_set_qibuild_python_path)
  if(WIN32)
    set(_pathsep ";")
  else()
    set(_pathsep ":")
  endif()
  set(_python_path $ENV{PYTHONPATH})
  string(REGEX MATCH
        "^${QIBUILD_PYTHON_PATH}${_pathsep}"
        _match
        "${_python_path}")
  if("${_match}" STREQUAL "")
    set(_python_path "${QIBUILD_PYTHON_PATH}${_pathsep}${_python_path}")
    set(ENV{PYTHONPATH} "${_python_path}")
  endif()
endfunction()

_set_qibuild_python_path()

#! Run a Python script
#
# Will call :cmake:function:`qi_error` if the return code of the script is not zero.
# If you need to get the output of the script as a CMake variable, use ::
#
#    qi_run_py_script(/path/to/my_script.py
#      OUTPUT_VARIABLE _out
#      OUTPUT_STRIP_TRAILING_WHITESPACE # optional, but may be handy
#    )
#    # do something with ``${_out}``
#
# \arg:script The path to the script
# \group:ARGUMENTS The arguments of the script (``sys.argv``)
#
function(qi_run_py_script script)
  if(NOT EXISTS "${script}")
    qi_error("${script} does not exist")
  endif()

  cmake_parse_arguments(ARG
    "OUTPUT_STRIP_TRAILING_WHITESPACE"
    "OUTPUT_VARIABLE"
    "ARGUMENTS"
    ""
    ${ARGN})

  if(NOT PYTHON2_EXECUTABLE)
    qi_error("Could not find Python executable")
  endif()


  set(_execute_process_args)
  if (ARG_OUTPUT_STRIP_TRAILING_WHITESPACE)
    list(APPEND _execute_process_args OUTPUT_STRIP_TRAILING_WHITESPACE)
  endif()

  if (ARG_OUTPUT_VARIABLE)
    list(APPEND _execute_process_args OUTPUT_VARIABLE ${ARG_OUTPUT_VARIABLE})
  endif()
  execute_process(COMMAND
    ${PYTHON2_EXECUTABLE} "${script}" ${ARG_ARGUMENTS}
                  ERROR_VARIABLE _err
                  RESULT_VARIABLE _rc
                  ${_execute_process_args}
                  )

  if(NOT ${_rc} EQUAL 0)
    qi_error("Calling Python script failed: ${_err}")
  endif()

  if (ARG_OUTPUT_VARIABLE)
    set(${ARG_OUTPUT_VARIABLE} ${${ARG_OUTPUT_VARIABLE}} PARENT_SCOPE)
  endif()

endfunction()


#! Run a Python program passed in as a string
# Behaves the same as :cmake:function:`qi_run_py_script`
# \arg:cmd: The Python code to run, as a string
function(qi_run_py_cmd cmd)
  cmake_parse_arguments(ARG
    ""
    "OUTPUT_VARIABLE"
    ""
    ${ARGN})
  set(_tmp_script_path "${CMAKE_CURRENT_BINARY_DIR}/qi_run_script_tmp.py")
  file(WRITE "${_tmp_script_path}" "${cmd}")
  set(_qi_run_py_script_args ${ARG_UNPARSED_ARGUMENTS})
  if (ARG_OUTPUT_VARIABLE)
    list(APPEND _qi_run_py_script_args OUTPUT_VARIABLE ${ARG_OUTPUT_VARIABLE})
  endif()

  qi_run_py_script(${_tmp_script_path}
    ${ARG_UNPARSED_ARGUMENTS}
    ${_qi_run_py_script_args})

  if (ARG_OUTPUT_VARIABLE)
    set(${ARG_OUTPUT_VARIABLE} ${${ARG_OUTPUT_VARIABLE}} PARENT_SCOPE)
  endif()
endfunction()


#! Create a python extension
function(qi_create_python_ext target)
  add_library(${target} SHARED ${ARGN})
  message(STATUS "Python extension: ${target}")
  set_target_properties(${target}
    PROPERTIES PREFIX ""
  )
  if(UNIX)
    set_target_properties(${target} PROPERTIES
      SUFFIX ".so"
      LIBRARY_OUTPUT_DIRECTORY ${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages
    )
  endif()

  if(WIN32)
    set_target_properties(${target} PROPERTIES
      SUFFIX ".pyd"
      RUNTIME_OUTPUT_DIRECTORY_RELEASE ${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages
      RUNTIME_OUTPUT_DIRECTORY_DEBUG ${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages
    )
  endif()

  qi_use_lib(${target} PYTHON)
  qi_install_python(TARGETS ${target} COMPONENT runtime)

  # Register the target into the build dir for qipy
  file(WRITE ${QI_SDK_DIR}/qi.pth
    "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages/\n"
  )
endfunction()
