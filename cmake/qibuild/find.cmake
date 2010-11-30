#
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics

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


# ####################################################################
# #
# # THIS FUNCTION IS DEPRECATED, prefer setting ${prefix}_DEPENDS
# #
# # append dependent lib to another one
# #
# ####################################################################
# function(depend prefix name0)
#   #warning(WARNING "LIBFIND: depend is deprecated, please dont use")
#   parse_is_options(_depend_modulelist "REQUIRED" _depend_is_required "${name0}" ${ARGN})
#   if(${_depend_is_required})
#     find_package(${_depend_modulelist} REQUIRED PATHS ${_INTERNAL_SDK_DIRS} NO_DEFAULT_PATH)
#   else(${_depend_is_required})
#     find_package(${_depend_modulelist} PATHS ${_INTERNAL_SDK_DIRS} NO_DEFAULT_PATH)
#   endif(${_depend_is_required})

#   qi_debug("FPKG: ${_depend_modulelist}")
#   qi_debug("FPKG: ${${prefix}_INCLUDE_DIR}")
#   qi_debug("FPKG: ${${_depend_modulelist}_INCLUDE_DIR}")
#   qi_debug("FPKG: ${${_depend_modulelist}_LIBRARIES}")

#   set(${prefix}_INCLUDE_DIR ${${prefix}_INCLUDE_DIR} ${${_depend_modulelist}_INCLUDE_DIR} CACHE STRING   "" FORCE)
#   set(${prefix}_LIBRARIES   ${${prefix}_LIBRARIES}   ${${_depend_modulelist}_LIBRARIES}   CACHE STRING   "" FORCE)
#   set(${prefix}_DEFINITIONS ${${prefix}_DEFINITIONS} ${${_depend_modulelist}_DEFINITIONS} CACHE STRING   "" FORCE)
# endfunction(depend)

include(CMakeParseArguments)

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

  find_path(${name0}_INCLUDE ${name0} ${ARG_UNPARSED_ARGUMENTS} HINTS ${FRAMEWORK_PREFIX} ${INCLUDE_PREFIX})

  if (${name0}_INCLUDE)
    set(${prefix}_INCLUDE_DIR ${${name0}_INCLUDE} ${${prefix}_INCLUDE_DIR} CACHE PATH "" FORCE)
  else()
    message(STATUS "[${prefix}] file_path ${name0} NOT FOUND")
  endif()

  #list(APPEND ${prefix}_INCLUDE_DIR "${${_modullelist}_INCLUDE}")
  qi_debug("LIBFIND: RESULT: ${${name0}_INCLUDE}")
  qi_debug("LIBFIND: ${prefix}_INCLUDE_DIR: ${${prefix}_INCLUDE_DIR}")
  set(${name0}_INCLUDE CACHE INTERNAL "" FORCE)
endfunction(fpath)



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

  set(${name}_LIB "${_name}_LIB-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)

  qi_debug("LIBFIND: PREFIX(system): ${LIB_PREFIX}")
  qi_debug("LIBFIND: PREFIX : ${LIB_EXTRA_PREFIX}")
  qi_debug("LIBFIND: modulelist: ${_flib_modulelist}")
  if (ARG_SYSTEM)
    qi_deprecated("Deprecated SYSTEM arguments")
  endif()
  find_library(${name}_LIB ${ARG_NAMES} PATHS ${FRAMEWORK_PREFIX} ${LIB_PREFIX})

  if (ARG_DEBUG)
    set(_keyword "debug")
  elseif (ARG_OPTIMIZED)
    set(_keyword "optimized")
  else()
    set(_keyword "general")
  endif()

  if (${name}_LIB)
    set(${prefix}_LIBRARIES ${_keyword} "${${name}_LIB}" ${${prefix}_LIBRARIES} CACHE STRING "" FORCE)
  else (${name}_LIB)
    message(STATUS "[${prefix}] Cannot find library: ${name} NOT FOUND")
  endif (${name}_LIB)

  #list(APPEND ${prefix}_LIBRARIES "${${_modulelist}_LIB}")
  qi_debug("LIBFIND: RESULT: ${${_modulelist}_LIB}")
  qi_debug("LIBFIND: ${prefix}_LIBRARIES: ${${prefix}_LIBRARIES}")
  set(${name}_LIB CACHE INTERNAL "" FORCE)
endfunction(flib)

##########################
# search a program
##########################
function(fprogram prefix name)
  qi_debug( "looking for ${name} in ${BIN_PREFIX}")
  find_program(${prefix} ${name} PATHS ${BIN_PREFIX})
endfunction()


####################################################################
#
# cleanup variable related to a library/executable/source-only library
#
####################################################################
function(clean prefix)
  set(${prefix}_INCLUDE_DIR ""    CACHE STRING   "Cleared." FORCE)
  set(${prefix}_LIBRARIES   ""    CACHE STRING   "Cleared." FORCE)
  set(${prefix}_DEFINITIONS ""    CACHE STRING   "Cleared." FORCE)
  set(${prefix}_EXECUTABLE  ""    CACHE STRING   "Cleared." FORCE)
  set(${prefix}_EXECUTABLE_DEBUG  ""    CACHE STRING   "Cleared." FORCE)
  set(${prefix}_SEARCHED    FALSE CACHE INTERNAL "Cleared." FORCE)
  mark_as_advanced(${prefix}_DEFINITIONS ${prefix}_INCLUDE_DIR ${prefix}_LIBRARIES ${prefix}_TARGET ${prefix}_EXECUTABLE ${prefix}_EXECUTABLE_DEBUG)
endfunction(clean)


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

  mark_as_advanced(${prefix}_DIR)
  #mark as already searched
  set(${prefix}_SEARCHED TRUE CACHE INTERNAL "" FORCE)

  if(${prefix}_INCLUDE_DIR AND ${prefix}_LIBRARIES)
    set(${prefix}_FOUND TRUE CACHE INTERNAL "" FORCE)
  endif(${prefix}_INCLUDE_DIR AND ${prefix}_LIBRARIES)

  if(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
    if(NOT ${prefix}_INCLUDE_DIR )
      message( STATUS "Required include not found : ${prefix}_INCLUDE_DIR")
      message( FATAL_ERROR "Could not find ${prefix} include!")
    endif( NOT ${prefix}_INCLUDE_DIR )
    if(NOT ${prefix}_LIBRARIES )
      message( STATUS "Required libraries not found : ${prefix}_LIBRARIES")
      message( FATAL_ERROR "Could not find ${prefix} libraries!")
    endif(NOT ${prefix}_LIBRARIES)
  endif(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
endfunction(export_lib)





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

  mark_as_advanced(${prefix}_DIR)
  #mark as already searched
  set(${prefix}_SEARCHED TRUE CACHE INTERNAL "" FORCE)

  if(${prefix}_EXECUTABLE)
    set(${prefix}_FOUND TRUE CACHE INTERNAL "" FORCE)
  endif(${prefix}_EXECUTABLE)

  if(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
    qi_info( STATUS "Required executable not found : ${prefix}_EXECUTABLE")
    qi_info( FATAL_ERROR "Could not find ${prefix} executable!")
  endif(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
endfunction(export_bin)

####################################################################
#
# export_header
#
####################################################################
function(export_header prefix)
  # Finally, display informations if not in quiet mode
  qi_verbose("header ${prefix}:" )
  qi_verbose("  includes   : ${${prefix}_INCLUDE_DIR}" )
  qi_verbose("  definitions: ${${prefix}_DEFINITIONS}" )

  mark_as_advanced(${prefix}_DIR)
  #mark as already searched
  set(${prefix}_SEARCHED TRUE CACHE INTERNAL "" FORCE)

  if(${prefix}_INCLUDE_DIR)
    set(${prefix}_FOUND TRUE CACHE INTERNAL "" FORCE)
  endif(${prefix}_INCLUDE_DIR)

  if(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
    qi_info( STATUS "Required include not found : ${prefix}_INCLUDE_DIR")
    qi_info( FATAL_ERROR "Could not find ${prefix} include!")
  endif(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
endfunction(export_header)

####################################################################
#
# find
#
####################################################################
#TODO: move aways
function(find)
  if (NOT ${ARGV0}_SEARCHED)
    find_package(${ARGN} PATHS "${SDK_DIR}/${_SDK_CMAKE_MODULES}/" ${_INTERNAL_SDK_DIRS} NO_DEFAULT_PATH)
  endif (NOT ${ARGV0}_SEARCHED)
endfunction(find)

