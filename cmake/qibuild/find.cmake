## Copyright (C) 2011 Aldebaran Robotics

#
# this file contain helper function to find library in cmake (you need it only for Find*.cmake files)
#
#
# exported FUNCTION:
#
# clean : clean variable for a library
# fpath : find a path (include) fpath(<VAR> [SYSTEM] [REQUIRED] name [PATH_SUFFIXES suffixes])
# flib  : find a library
# depend: add a dependency
# export: export variable and verify the validity of the lib
#

if (_QI_LIBFIND_CMAKE_)
  return()
endif()
set(_QI_LIBFIND_CMAKE_ TRUE)


include(CMakeParseArguments)
include(FindPackageHandleStandardArgs)

# Helper function to call FPHSA
# \flag: HEADER : just a header was searched,
#                      only ${prefix}_INCLUDE_DIRS will be set.
# \flag: EXECUTABLE : just an executable was searched,
#                      only ${prefix}_EXECUTABLE will be set.
function(_qi_call_fphsa prefix)
  set(${prefix}_FIND_REQUIRED TRUE)
  set(${prefix}_FIND_QUIETLY TRUE)
  cmake_parse_arguments(ARG "HEADER;EXECUTABLE" "" "" ${ARGN})

  set(_to_check)
  if(ARG_HEADER)
    set(_to_check ${prefix}_INCLUDE_DIR)
  elseif(ARG_EXECUTABLE)
    set(_to_check ${prefix}_EXECUTABLE)
  else()
    set(_to_check ${prefix}_LIBRARIES ${prefix}_INCLUDE_DIR)
  endif()
  find_package_handle_standard_args(${prefix} DEFAULT_MSG ${_to_check})
endfunction()


####################################################################
#
#search a path
#
####################################################################
function(fpath prefix name0)
  qi_debug("LIBFIND: FPATH (prefix=${prefix}, name0=${name0})")
  cmake_parse_arguments(ARG "SYSTEM" "" "" ${ARGN})

  set(${name0}_INCLUDE "${name0}_INCLUDE-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)
  mark_as_advanced(${name0}_INCLUDE)
  if (ARG_SYSTEM)
    qi_deprecated("You should not use fpath(SYSTEM) anymore")
  endif()

  find_path(${name0}_INCLUDE ${name0} ${ARG_UNPARSED_ARGUMENTS})

  if (${name0}_INCLUDE)
    set(${prefix}_INCLUDE_DIR ${${name0}_INCLUDE} ${${prefix}_INCLUDE_DIR} CACHE PATH "" FORCE)
  else()
    message(STATUS "[${prefix}] file_path ${name0} NOT FOUND")
  endif()

  #list(APPEND ${prefix}_INCLUDE_DIR "${${_modullelist}_INCLUDE}")
  qi_debug("LIBFIND: RESULT: ${${name0}_INCLUDE}")
  qi_debug("LIBFIND: ${prefix}_INCLUDE_DIR: ${${prefix}_INCLUDE_DIR}")
  set(${name0}_INCLUDE CACHE INTERNAL "" FORCE)
endfunction()



####################################################################
#
# search a library
#
# /!\ If you call flib with DEBUG as a keyword argument, you MUST also
# call flib with RELEASE as a keyword argument.
#
# TODO: find a way to check this ...
####################################################################
function(flib prefix)
  qi_debug("LIBFIND: FLIB (prefix=${prefix}, name=${name})")
  cmake_parse_arguments(ARG "DEBUG;OPTIMIZED;REQUIRED;SYSTEM" "" "NAMES" ${ARGN})

  set(ARG_NAMES ${ARG_UNPARSED_ARGUMENTS} ${ARG_NAMES})
  list(GET ARG_NAMES 0 name)

  #qi_info("ARG_NAMES: ${ARG_NAMES} , name: ${name}")
  if ("${name}" STREQUAL "")
    qi_error("empty name: ${name}")
  endif()

  set(${name}_LIB "${name}_LIB-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)

  qi_debug("LIBFIND: modulelist: ${_flib_modulelist}")
  if (ARG_SYSTEM)
    qi_deprecated("Deprecated SYSTEM arguments")
  endif()
  find_library(${name}_LIB "${name}" NAMES ${ARG_NAMES})

  if (ARG_DEBUG)
    set(_keyword "debug")
  elseif (ARG_OPTIMIZED)
    set(_keyword "optimized")
  else()
    set(_keyword "general")
  endif()

  if (${name}_LIB)
    set(${prefix}_LIBRARIES ${_keyword} "${${name}_LIB}" ${${prefix}_LIBRARIES} CACHE STRING "" FORCE)
  else()
    message(STATUS "[${prefix}] Cannot find library: ${name} NOT FOUND")
  endif()

  #list(APPEND ${prefix}_LIBRARIES "${${_modulelist}_LIB}")
  qi_debug("LIBFIND: RESULT: ${${_modulelist}_LIB}")
  qi_debug("LIBFIND: ${prefix}_LIBRARIES: ${${prefix}_LIBRARIES}")
  set(${name}_LIB CACHE INTERNAL "" FORCE)
endfunction()

####################################################################
#
# cleanup variable related to a library/executable/source-only library
#
####################################################################
function(clean prefix)
  set(${prefix}_INCLUDE_DIR ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_LIBRARIES   ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_DEFINITIONS ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_EXECUTABLE  ""           CACHE STRING   "Cleared." FORCE)
  set(${prefix}_EXECUTABLE_DEBUG  ""     CACHE STRING   "Cleared." FORCE)
  set(${prefix}_SEARCHED    FALSE        CACHE INTERNAL "Cleared." FORCE)
  mark_as_advanced(${prefix}_DEFINITIONS ${prefix}_INCLUDE_DIR ${prefix}_LIBRARIES ${prefix}_TARGET ${prefix}_EXECUTABLE ${prefix}_EXECUTABLE_DEBUG)
endfunction()


####################################################################
#
# export_lib
#
####################################################################
function(export_lib prefix)
  # Finally, display informations if not in quiet mode
  qi_verbose("library ${prefix}:" )
  qi_verbose("  includes   : ${${prefix}_INCLUDE_DIR}" )
  qi_verbose("  libraries  : ${${prefix}_LIBRARIES}" )
  qi_verbose("  definitions: ${${prefix}_DEFINITIONS}" )

  _qi_call_fphsa(${prefix})
endfunction()



####################################################################
#
# export_bin
#
####################################################################
function(export_bin prefix)
  # Finally, display informations if not in quiet mode
  qi_verbose("Tools ${prefix}:" )
  qi_verbose("  executable  : ${${prefix}_EXECUTABLE}" )
  qi_verbose("  executable_d: ${${prefix}_EXECUTABLE_DEBUG}" )

  _qi_call_fphsa(${prefix} EXECUTABLE)
endfunction()

####################################################################
#
# export_header
#
####################################################################
function(export_header prefix)
  _qi_call_fphsa(${prefix} HEADER)
endfunction()

