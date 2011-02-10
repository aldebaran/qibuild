## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild UseLib
# ===============
#
# == Overview ==
# qi_use_lib handle dependencies between projects.
# It will call find_package for you, then do all include_directories
# and target_link_libraries needed.
# \example:uselib
#

if (_QI_USELIB_CMAKE_)
  return()
endif()
set(_QI_USELIB_CMAKE_ TRUE)

#compute the dependencies list, removing duplicate
#TODO: store computed dependencies in ${_U_PKG}_FLAT_DEPENDS ?
function(_qi_use_lib_get_deps _OUT_list)
  set(_result ${ARGN})
  list(LENGTH _result _count)
  if (_count EQUAL 0)
    return()
  endif()

  foreach(_pkg ${ARGN})
    string(TOUPPER ${_pkg} _U_PKG)
    if (NOT ${_U_PKG}_SEARCHED)
      find_package(${_pkg} ${_is_required})
      qi_set_global("${_U_PKG}_SEARCHED" TRUE)
    endif()

    foreach(_sub_dep ${${_U_PKG}_DEPENDS})
      list(FIND _result ${_sub_dep} _is_present)
      if (_is_present EQUAL -1)
        _qi_use_lib_get_deps(_new_deps "${_sub_dep}")
        list(APPEND _result ${_new_deps})
      endif()
    endforeach()
  endforeach()

  list(REMOVE_DUPLICATES _result)

  set(${_OUT_list} ${_result} PARENT_SCOPE)
endfunction()


#!
# Find dependencies and add them to the target <name>.
# This will call include_directories with XXX_INCLUDE_DIRS or fallback to XXX_INCLUDE_DIR
# This will call target_link_libraries with XXX_LIBRARIES or fallback to XXX_LIBRARY
#
# \arg:name the target to add dependencies to
# \flag:OPTIONAL do not stop on error
# \group:DEPENDENCIES the list of dependencies
function(qi_use_lib name)
  cmake_parse_arguments(ARG "OPTIONAL" "PLATEFORM" "DEPENDS" ${ARGN})

  set(_is_required "REQUIRED")
  if (ARG_OPTIONAL)
    set(_is_required "")
  endif()

  set(ARG_DEPENDS ${ARG_UNPARSED_ARGUMENTS} ${ARG_DEPENDS})

  _qi_use_lib_get_deps(_DEPS ${ARG_DEPENDS})

  foreach(_pkg ${_DEPS})
    string(TOUPPER ${_pkg} _U_PKG)

    if (DEFINED ${_U_PKG}_INCLUDE_DIRS)
      include_directories(${${_U_PKG}_INCLUDE_DIRS})
    elseif(DEFINED ${_U_PKG}_INCLUDE_DIR)
      include_directories(${${_U_PKG}_INCLUDE_DIR})
    endif()

    if (DEFINED ${_U_PKG}_LIBRARIES)
      target_link_libraries("${name}" ${${_U_PKG}_LIBRARIES})
    elseif (DEFINED ${_U_PKG}_LIBRARY)
      target_link_libraries("${name}" ${${_U_PKG}_LIBRARY})
    endif()

    if ( (DEFINED "${_U_PKG}_TARGET") AND (TARGET "${${_U_PKG}_TARGET}") )
      add_dependencies(${name} "${${_U_PKG}_TARGET}")
    endif()
    if(${_U_PKG}_DEFINITIONS)
      # Append the correct compile definitions to the target
      set(_to_add)
      get_target_property(_compile_defs ${name} COMPILE_DEFINITIONS)
      if(_compile_defs)
        set(_to_add ${_compile_defs})
      endif()

      set(_to_add "${_to_add} ${${_U_PKG}_DEFINITIONS}")
      if(_to_add)
        set_target_properties(${name}
          PROPERTIES
            COMPILE_DEFINITIONS ${_to_add})
      endif()
    endif()
  endforeach()
  string(TOUPPER "${name}" _U_name)
  qi_set_global("${_U_name}_DEPENDS" ${${_U_name}_DEPENDS} ${_DEPS})
endfunction()
