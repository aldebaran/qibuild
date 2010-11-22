####
# cpackutils.cmake
#
# CPack is buggy.
# You can't include cpack twice, you have to set all CPACK_* variables
# before include cpack

# Usage:
#   simply call generate_cpack_component_install()
# Do NOT include(CPack) afetwards.


set(CPACK_ALL_INSTALL_TYPES)
set(CPACK_COMPONENTS_ALL)

##
# _cpack_add_install_type( INSTALL_TYPE "DESCRIPTION ...")
function(_cpack_add_install_type _name)
  list(APPEND CPACK_ALL_INSTALL_TYPES ${_name})
  set(CPACK_ALL_INSTALL_TYPES ${CPACK_ALL_INSTALL_TYPES} PARENT_SCOPE)
  set(CPACK_INSTALL_TYPE_${_name}_DISPLAY_NAME ${ARGN})
endfunction()

##
# _cpack_add_component_group( GROUP_NAME [EXPANDED] "DESCRIPTION ...")
function(_cpack_add_component_group _name)
  string(TOUPPER ${_name} _name_upper)
  set(CPACK_COMPONENT_${_name_upper}_GROUP ${_name} PARENT_SCOPE)
  parse_is_options(_args0 EXPANDED _is_expanded ${ARGN})
  if(_is_expanded)
    set(CPACK_COMPONENT_${_name_upper}_EXPANDED PARENT_SCOPE)
  endif()
  set(CPACK_COMPONENT_${_name_upper}_GROUP_DESCRIPTION ${args0} PARENT_SCOPE)
endfunction()

##
# _cpack_add_component( COMPNAME
# [DISPLAY_NAME "display name"]
# [DESCRIPTION "DESCRIPTION"]
# [GROUP group]
function(_cpack_add_component _name)
  string(TOUPPER ${_name} _name_upper)
  parse_option_with_arg(DISPLAY_NAME _display_name args0 ${ARGN})
  parse_option_with_arg(DESCRIPTION  _description  args1 ${args0})
  parse_option_with_arg(GROUP        _group        args2 ${args1})

  set(CPACK_COMPONENT_${_name_upper}_DISPLAY_NAME ${_display_name} PARENT_SCOPE)
  set(CPACK_COMPONENT_${_name_upper}_DESCRIPTION  ${_description}  PARENT_SCOPE)
  set(CPACK_COMPONENT_${_name_upper}_GROUP        ${_group}        PARENT_SCOPE)
  list(APPEND CPACK_COMPONENTS_ALL ${_name})
  set(CPACK_COMPONENTS_ALL ${CPACK_COMPONENTS_ALL} PARENT_SCOPE)
endfunction()

##
# _cpack_set_component_install_types(COMPANME INST_TYPES ...)
function(_cpack_set_component_install_types _name)
  string(TOUPPER ${_name} _name_upper)
  set(CPACK_COMPONENT_${_name_upper}_INSTALL_TYPES ${ARGN} PARENT_SCOPE)
endfunction()

##
# _cpack_set_component_deps(COMPANME DEPS ...)
function(_cpack_set_component_deps _name)
  string(TOUPPER ${_name} _name_upper)
  set(CPACK_COMPONENT_${_name_upper}_DEPENDS ${ARGN} PARENT_SCOPE)
endfunction()


###############################
# Call this and never include cpack afterwards
# CPACK COMPONENT:
# Runtime:
#  binary
#  lib
#  conf
#  data
#  python
#
# Dev:
#  static_lib
#  header
#  cmake
#
# Doc:
#  doc
###############################
function(generate_cpack_config)
  # Installation types
  _cpack_add_install_type(Normal    "Standard installation")
  _cpack_add_install_type(Developer "Developer installation")

  # Component groups
  _cpack_add_component_group(Runtime       DESCRIPTION "Our amazing binaries!")
  _cpack_add_component_group(Development   EXPANDED DESCRIPTION "All of the tools you'll ever need to develop software")
  _cpack_add_component_group(Documentation EXPANDED DESCRIPTION "All the documentation you would expect")

  # Applications
  _cpack_add_component(binary
    DISPLAY_NAME "Applications"
    DESCRIPTION "All application"
    GROUP Runtime)

  _cpack_add_component(conf
    DISPLAY_NAME "Applications"
    DESCRIPTION "All application"
    GROUP Runtime)

  _cpack_add_component(data
    DISPLAY_NAME "data"
    DESCRIPTION "Data needed by applications"
    GROUP Runtime)

  _cpack_add_component(lib
    DISPLAY_NAME "Libraries"
    DESCRIPTION "Libraries needed by programs"
    GROUP Runtime)

  _cpack_add_component(python
    DISPLAY_NAME "Pythons"
    DESCRIPTION "Python support"
    GROUP Runtime)

  # Development
  _cpack_add_component(static_lib
    DISPLAY_NAME "Libraries"
    DESCRIPTION "Static libraries used to build programs"
    GROUP Development)

  _cpack_add_component(header
    DISPLAY_NAME "C/C++ Headers"
    DESCRIPTION "C/C++ header files"
    GROUP Development)

  _cpack_add_component(cmake
    DISPLAY_NAME "CMake"
    DESCRIPTION "CMake support"
    GROUP Development)

  #Documentation
  _cpack_add_component(doc
    DISPLAY_NAME "Documentations"
    DESCRIPTION "Documentation files"
    GROUP Documentation)

  _cpack_add_component(thirdparty
    DISPLAY_NAME "Third Party software"
    DESCRIPTION  "Third Party software"
    GROUP Development)

  #_cpack_set_component_deps(header lib)
  #_cpack_set_component_deps(cmake  lib)

  _cpack_set_component_install_types(binary      Developer Normal)
  _cpack_set_component_install_types(conf        Developer Normal)
  _cpack_set_component_install_types(data        Developer Normal)
  _cpack_set_component_install_types(lib         Developer Normal)
  _cpack_set_component_install_types(python      Developer Normal)
  _cpack_set_component_install_types(thirdparty  Developer Normal)
  _cpack_set_component_install_types(static_lib  Developer       )
  _cpack_set_component_install_types(cmake       Developer       )
  _cpack_set_component_install_types(header      Developer       )
  _cpack_set_component_install_types(doc         Developer       )

  if(_CPACK_INCLUDED)
    return()
  else()
    include(CPack)
    set(_CPACK_INCLUDED TRUE CACHE BOOL "" FORCE)
  endif()
endfunction()


##
# Usage:
# supposing you have your msi files in package/thirdparty/foo.msi,
# You should be able to configure CPack by using a cmakelists.txt
# looking like:
#
#     Cmake commands ...
#
#     Setting of some CPACK_* variables here ....
#
#     add_third_party_msi(name msi_file)
#     generate_cpack_config()
#
# Note: the name is only used to display a pop-up asking the
# user if he wants to install "foo"
# the name of the msi should just be "foo.msi"
#
# TODO:
#    Use only one argument, the path to the msi_file.
function(add_third_party_msi _name _msi_file)
  if(NOT WIN32)
    return()
  endif()
  install(FILES
    "package/thirdparty/${_msi_file}"
    COMPONENT "thirdparty"
    DESTINATION
    "thirdparty"
  )

  # Really tricky escapes happen here.
  # Do not change unless you know what you're doing
  set(_nsis_code_in
  "
    ; Install @_name@
    SetOutPath \\\"$INSTDIR\\\\thirdparty\\\"
      MessageBox MB_YESNO 'Install @_name@?' /SD IDYES IDNO end@_name@Inst
      ExecWait 'msiexec /i \\\"@_msi_file@\\\"'
      Goto end@_name@Inst
    end@_name@Inst:
  "
  )
  string(CONFIGURE "${_nsis_code_in}" _nsis_code_out @ONLY ESCAPE_QUOTES)
  set(CPACK_NSIS_EXTRA_INSTALL_COMMANDS
    "${CPACK_NSIS_EXTRA_INSTALL_COMMANDS} ${_nsis_code_out}"
    PARENT_SCOPE
  )
endfunction()


# Ditto, for .exe files
# TODO: factor this!
function(add_third_party_exe _name _exe_file)
  if(NOT WIN32)
    return()
  endif()
  install(FILES
    "package/thirdparty/${_exe_file}"
    COMPONENT "thirdparty"
    DESTINATION
    "thirdparty"
  )
  set(_nsis_code_in
  "
    ; Install @_name@
    SetOutPath \\\"$INSTDIR\\\\thirdparty\\\"
      MessageBox MB_YESNO 'Install @_name@?' /SD IDYES IDNO end@_name@Inst
      ExecWait \\\"@_exe_file@\\\"
      Goto end@_name@Inst
    end@_name@Inst:
  "
  )
  string(CONFIGURE "${_nsis_code_in}" _nsis_code_out @ONLY ESCAPE_QUOTES)
  set(CPACK_NSIS_EXTRA_INSTALL_COMMANDS
    "${CPACK_NSIS_EXTRA_INSTALL_COMMANDS} ${_nsis_code_out}"
    PARENT_SCOPE
  )


endfunction()


