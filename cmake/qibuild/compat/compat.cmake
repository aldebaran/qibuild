##
## Author(s):
##  - Cedric GESTES <cgestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010, 2011 Cedric GESTES
##

function(sdk_add_include _name _subfolder)
  qi_deprecated("no implementation")
endfunction(sdk_add_include _name _subfolder)

######################
# Install
######################
function(install_header _name)
  qi_deprecated("no implementation")
endfunction(install_header _name)

function(install_data _subfolder)
  qi_deprecated("no implementation")
endfunction(install_data _name)

function(install_data_dir _subfolder)
  qi_deprecated("no implementation")
endfunction(install_data_dir)

function(install_doc _subfolder)
  qi_deprecated("no implementation")
endfunction(install_doc _name)

function(install_conf _subfolder)
  qi_deprecated("no implementation")
endfunction(install_conf _name)

function(install_cmake _subfolder)
  qi_deprecated("no implementation")
endfunction()

######################
# Target
######################
function(create_bin _name)
  qi_deprecated("no implementation")
endfunction(create_bin)

function(create_script _name _namein)
  qi_deprecated("no implementation")
endfunction(create_script)

function(create_lib _name)
  qi_deprecated("no implementation")
endfunction(create_lib)

function(create_config_h _header _nameout)
  qi_deprecated("unimplemented")
endfunction(create_config_h)

function(create_gtest _name)
  qi_deprecated("unimplemented")
endfunction()

function(create_cmake _NAME)
  qi_deprecated("unimplemented")
endfunction()

function(use _NAME)
  qi_deprecated("unimplemented")
endfunction()

function(use_lib _name)
  qi_deprecated("unimplemented")
endfunction()

######################
# Log
######################
function(debug)
  qi_deprecated()
  qi_debug(${ARGN})
endfunction(debug)

function(verbose)
  qi_deprecated()
  qi_verbose(${ARGN})
endfunction(verbose)

function(info)
  qi_deprecated()
  qi_info(${ARGN})
endfunction(info)

function(warning)
  qi_deprecated()
  qi_warning(${ARGN})
endfunction(warning)

function(error)
  qi_deprecated()
  qi_error(${ARGN})
endfunction(error)

#####################
# stage
#####################
function(stage_lib _targetname _name)
  qi_deprecated("unimplemented")
endfunction(stage_lib _targetname _name)

function(stage_script _file _name)
  qi_deprecated("unimplemented")
endfunction(stage_script)

function(stage_bin _targetname _name)
  qi_deprecated("unimplemented")
endfunction(stage_bin)

function(stage_header _name)
  qi_deprecated("unimplemented")
endfunction(stage_header)

function(cond_subdirectory subdir)
  qi_deprecated("unimplemented")
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

