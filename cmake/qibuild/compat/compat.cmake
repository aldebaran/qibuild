##
## Author(s):
##  - Cedric GESTES <cgestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010, 2011 Cedric GESTES
##

function(sdk_add_include _name _subfolder)
  qi_deprecated("no implementation")
endfunction()

######################
# Install
######################
function(install_header)
  qi_deprecated("install_header is deprecated.
  Use qi_install_header instead")
  qi_install_header(${ARGN})
endfunction()

function(install_data)
  qi_deprecated("install_data is deprecated.
  Use qi_install_data instead")
  qi_install_data(${ARGN})
endfunction()

function(install_data_dir _subfolder)
  qi_deprecated("no implementation")
endfunction()

function(install_doc)
  qi_deprecated("install_doc is deprecated.
  Use qi_install_doc instead")
  qi_install_doc(${ARGN})
endfunction()

function(install_conf)
  qi_deprecated("install_conf is deprecated.
  Use qi_install_conf instead")
  qi_install_conf(${ARGN})
endfunction()

function(install_cmake)
  qi_deprecated("install_cmake is deprecated.
  Use qi_install_cmake instead")
  qi_install_cmake(${ARGN})
endfunction()

######################
# Target
######################
function(create_bin)
  qi_deprecated("create_bin is deprecated:
    use qi_create_bin instead
  ")
  qi_create_bin(${ARGN})
endfunction()

function(create_script)
  qi_deprecated("create_script is deprecated:
    use qi_create_script instead")
  qi_create_script(${ARGN})
endfunction()

function(create_lib)
  qi_deprecated("create_lib is deprecated:
    use qi_create_lib instead")
  qi_create_lib(${ARGN})
endfunction()

function(create_config_h)
  qi_deprecated("create_config_h is deprecated:
    use qi_create_config_h instead")
  qi_create_config_h(${ARGN})
endfunction()

function(create_gtest)
  qi_deprecated("create_gtest is deprecated:
    use qi_create_gtest instead")
  qi_create_gtest(${ARGN})
endfunction()

function(create_cmake _NAME)
  qi_deprecated("create_cmake is deprecated:
    Simply put you cmake code in you_project/cmake/modules
  ")
endfunction()

function(use _NAME)
  qi_deprecated("use is deprecated:
    Use the regular include() function instead
  ")
endfunction()

function(use_lib)
  qi_use_lib("use qi_use_lib instead.
    Note that the names can be target names.

    For instance, intead of:

      create_lib(foo foo.cpp)

      stage_lib(foo FOO)

      use_lib(bar FOO)


    you can do:
      qi_create_lib(foo foo.cpp)

      qi_stage_lib(foo)

      qi_use_lib(bar foo)
  ")
  qi_use_lib(${ARGN})

endfunction()

######################
# Log
######################
function(debug)
  qi_deprecated("debug is deprecated:
    Use qi_debug instead:
  ")
  qi_debug(${ARGN})
endfunction()

function(verbose)
  qi_deprecated("verbose is deprecated:
    Use qi_verbose instead:
  ")
  qi_verbose(${ARGN})
endfunction()

function(info)
  qi_deprecated("info is deprecated:
    Use qi_info instead:
  ")
  qi_info(${ARGN})
endfunction()

function(warning)
  qi_deprecated("warning is deprecated:
    Use qi_warning instead:
  ")
  qi_warning(${ARGN})
endfunction()

function(error)
  qi_deprecated("error is deprecated:
    Use qi_error instead:
  ")
  qi_error(${ARGN})
endfunction()

#####################
# stage
#####################
function(stage_lib _targetname _name)
  qi_deprecated("stage_lib is deprecated:
    Use qi_stage_lib instead.

    Warning the signature has changed:

    Instead of:

      create_lib(foo foo.cpp)

      stage_lib(foo FOO)

    Use:

      qi_create_lib(foo foo.cpp)

      # No need for upper-case \"stage name\"
      # anymore:
      qi_stage_lib(foo)

  ")
  string(TOUPPER ${_targetname} _U_targetname)
  if (NOT ${_U_targetname} STREQUAL ${_name})
    warning("
      Not using stage_lib(foo FOO) where the second
      argument if not equals to the upper-version of the first
      argument is not supported anymore.

      Please replace:
      stage_lib(${_targetname} ${_U_targetname})

      instead of:
      stage_lib(${_targetname} ${name})
    "
    )
    # FIXME: stage the lib with an other name ...
  endif()
  qi_stage_lib(${_targetname} ${ARGN})
endfunction()

function(stage_script _file _name)
  qi_deprecated("unimplemented")
endfunction()

function(stage_bin _targetname _name)
  qi_deprecated("unimplemented")
endfunction()

function(stage_header _name)
  qi_deprecated("unimplemented")
endfunction()

function(cond_subdirectory)
  qi_deprecated("cond_subdirectory is deprecated.
  Use qi_add_subdirectory() instead.

  ")
  qi_add_subdirectory(${ARGN})
endfunction()

function(add_python_test _name _pythonFile)
  qi_deprecated("unimplemented")
endfunction()

function(gen_trampoline _binary_name _trampo_name)
  qi_deprecated("unimplemented")
endfunction()

function(gen_sdk_trampoline _binary_name _trampo_name)
  qi_deprecated("unimplemented")
endfunction()

# hack:
function(add_msvc_precompiled_header)
  warning("add_msvc_precompiled_header not implemented yet")
endfunction()
