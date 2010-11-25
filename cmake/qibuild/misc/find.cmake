#
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

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

if (NOT _LIBFIND_CMAKE_)
set(_LIBFIND_CMAKE_ TRUE)

include("${T001CHAIN_DIR}/cmake/plateform.cmake")


####################################################################
#
# THIS FUNCTION IS DEPRECATED, prefer setting ${prefix}_DEPENDS
#
# append dependent lib to another one
#
####################################################################
function(depend prefix name0)
  #warning(WARNING "LIBFIND: depend is deprecated, please dont use")
  parse_is_options(_depend_modulelist "REQUIRED" _depend_is_required "${name0}" ${ARGN})
  if(${_depend_is_required})
    find_package(${_depend_modulelist} REQUIRED PATHS ${_INTERNAL_SDK_DIRS} NO_DEFAULT_PATH)
  else(${_depend_is_required})
    find_package(${_depend_modulelist} PATHS ${_INTERNAL_SDK_DIRS} NO_DEFAULT_PATH)
  endif(${_depend_is_required})

  debug("FPKG: ${_depend_modulelist}")
  debug("FPKG: ${${prefix}_INCLUDE_DIR}")
  debug("FPKG: ${${_depend_modulelist}_INCLUDE_DIR}")
  debug("FPKG: ${${_depend_modulelist}_LIBRARIES}")

  set(${prefix}_INCLUDE_DIR ${${prefix}_INCLUDE_DIR} ${${_depend_modulelist}_INCLUDE_DIR} CACHE STRING   "" FORCE)
  set(${prefix}_LIBRARIES   ${${prefix}_LIBRARIES}   ${${_depend_modulelist}_LIBRARIES}   CACHE STRING   "" FORCE)
  set(${prefix}_DEFINITIONS ${${prefix}_DEFINITIONS} ${${_depend_modulelist}_DEFINITIONS} CACHE STRING   "" FORCE)
endfunction(depend)



####################################################################
#
#search a path
#
####################################################################
function(fpath prefix name0)
  debug("LIBFIND: FPATH (prefix=${prefix}, name0=${name0})")
  parse_is_options(_arg1             "REQUIRED" _fpath_is_required "${name0}" ${ARGN})
  parse_is_options(_fpath_modulelist "SYSTEM"   _fpath_is_system   "${name0}" ${ARGN})

  set(${name0}_INCLUDE "${name0}_INCLUDE-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)
  mark_as_advanced(${name0}_INCLUDE)
  if (${_fpath_is_system})
    debug("LIBFIND: PREFIX(system): ${INCLUDE_PREFIX};${INCLUDE_EXTRA_PREFIX}")
    debug("LIBFIND: modulelist: ${name0}")
    debug("LIBFIND: yala:     find_path(${name0}_INCLUDE ${name0} PATHS ${INCLUDE_PREFIX} ${INCLUDE_EXTRA_PREFIX} NO_DEFAULT_PATH)")

    find_path(${name0}_INCLUDE ${_fpath_modulelist} PATHS ${INCLUDE_EXTRA_PREFIX} ${FRAMEWORK_PREFIX} ${INCLUDE_PREFIX} NO_DEFAULT_PATH)

  else (${_fpath_is_system})
    debug("LIBFIND: PREFIX: ${INCLUDE_PREFIX}")
    find_path(${name0}_INCLUDE ${_fpath_modulelist} PATHS ${FRAMEWORK_PREFIX} ${INCLUDE_PREFIX} NO_DEFAULT_PATH)
  endif (${_fpath_is_system})

  if (${name0}_INCLUDE)
    set(${prefix}_INCLUDE_DIR ${${name0}_INCLUDE} ${${prefix}_INCLUDE_DIR} CACHE PATH "" FORCE)
  else (${name0}_INCLUDE)
    message(STATUS "LIBFIND: [${prefix}] ${name0} NOT FOUND")
  endif (${name0}_INCLUDE)

  #list(APPEND ${prefix}_INCLUDE_DIR "${${_modullelist}_INCLUDE}")
  debug("LIBFIND: RESULT: ${${name0}_INCLUDE}")
  debug("LIBFIND: ${prefix}_INCLUDE_DIR: ${${prefix}_INCLUDE_DIR}")
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
function(flib prefix name)
  debug("LIBFIND: FLIB (prefix=${prefix}, name=${name})")
  parse_is_options(_arg0            "DEBUG"    _flib_is_debug    "${name}" ${ARGN})
  parse_is_options(_arg1            "OPTIMIZED"    _flib_is_optimized ${_arg0})
  #parse_is_options(_arg1            "REQUIRED" _flib_is_required "${name0}" ${_arg0})
  parse_is_options(_flib_modulelist "SYSTEM"   _flib_is_system   ${_arg1})

  list(GET _flib_modulelist 0 mname)
  if (mname STREQUAL "NAMES")
    list(GET _flib_modulelist 1 name0)
  else (mname STREQUAL "NAMES")
    list(GET _flib_modulelist 0 name0)
  endif (mname STREQUAL "NAMES")

  # info("modlist is :${_flib_modulelist}")
  # info("name0 is :${name0}")
  set(${name0}_LIB "${_name0}_LIB-NOTFOUND" CACHE INTERNAL "Cleared." FORCE)

  debug("LIBFIND: PREFIX(system): ${LIB_PREFIX}")
  debug("LIBFIND: PREFIX : ${LIB_EXTRA_PREFIX}")
  debug("LIBFIND: modulelist: ${_flib_modulelist}")
  if (${_flib_is_system})
    debug("LIBFIND: yala: find_library(${name0}_LIB ${_flib_modulelist} PATHS ${LIB_EXTRA_PREFIX} ${LIB_PREFIX} NO_DEFAULT_PATH)")
    find_library(${name0}_LIB ${_flib_modulelist} PATHS ${FRAMEWORK_PREFIX} ${LIB_EXTRA_PREFIX} ${LIB_PREFIX} NO_DEFAULT_PATH)
  else (${_flib_is_system})
    debug("LIBFIND: yala: find_library(${name0}_LIB ${_flib_modulelist} PATHS ${LIB_PREFIX} NO_DEFAULT_PATH)")
    find_library(${name0}_LIB ${_flib_modulelist} PATHS ${FRAMEWORK_PREFIX} ${LIB_PREFIX} NO_DEFAULT_PATH)
  endif (${_flib_is_system})

  if (${name0}_LIB)
    if(${_flib_is_debug} OR ${_flib_is_optimized})
      if(${_flib_is_debug})
        set(_keyword "debug")
      else(${_flib_is_debug})
        set(_keyword "optimized")
      endif(${_flib_is_debug})
    else(${_flib_is_debug} OR ${_flib_is_optimized})
      set(_keyword "general")
    endif(${_flib_is_debug} OR ${_flib_is_optimized})
    set(${prefix}_LIBRARIES ${_keyword} "${${name0}_LIB}" ${${prefix}_LIBRARIES} CACHE STRING "" FORCE)
  else (${name0}_LIB)
    message(STATUS "LIBFIND: [${prefix}] ${name0} NOT FOUND")
  endif (${name0}_LIB)

  #list(APPEND ${prefix}_LIBRARIES "${${_modulelist}_LIB}")
  debug("LIBFIND: RESULT: ${${_modulelist}_LIB}")
  debug("LIBFIND: ${prefix}_LIBRARIES: ${${prefix}_LIBRARIES}")
  set(${name0}_LIB CACHE INTERNAL "" FORCE)
endfunction(flib)

##########################
# search a program
##########################
function(fprogram prefix name)
  debug( "looking for ${name} in ${BIN_PREFIX}")
  find_program(${prefix} ${name} PATHS ${BIN_PREFIX} NO_DEFAULT_PATH)
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
  verbose("library ${prefix}:" )
  verbose("  includes   : ${${prefix}_INCLUDE_DIR}" )
  verbose("  libraries  : ${${prefix}_LIBRARIES}" )
  verbose("  definitions: ${${prefix}_DEFINITIONS}" )

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
  verbose("Tools ${prefix}:" )
  verbose("  executable  : ${${prefix}_EXECUTABLE}" )
  verbose("  executable_d: ${${prefix}_EXECUTABLE_DEBUG}" )

  mark_as_advanced(${prefix}_DIR)
  #mark as already searched
  set(${prefix}_SEARCHED TRUE CACHE INTERNAL "" FORCE)

  if(${prefix}_EXECUTABLE)
    set(${prefix}_FOUND TRUE CACHE INTERNAL "" FORCE)
  endif(${prefix}_EXECUTABLE)

  if(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
    message( STATUS "Required executable not found : ${prefix}_EXECUTABLE")
    message( FATAL_ERROR "Could not find ${prefix} executable!")
  endif(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
endfunction(export_bin)

####################################################################
#
# export_header
#
####################################################################
function(export_header prefix)
  # Finally, display informations if not in quiet mode
  verbose("header ${prefix}:" )
  verbose("  includes   : ${${prefix}_INCLUDE_DIR}" )
  verbose("  definitions: ${${prefix}_DEFINITIONS}" )

  mark_as_advanced(${prefix}_DIR)
  #mark as already searched
  set(${prefix}_SEARCHED TRUE CACHE INTERNAL "" FORCE)

  if(${prefix}_INCLUDE_DIR)
    set(${prefix}_FOUND TRUE CACHE INTERNAL "" FORCE)
  endif(${prefix}_INCLUDE_DIR)

  if(NOT ${prefix}_FOUND AND ${prefix}_FIND_REQUIRED)
    message( STATUS "Required include not found : ${prefix}_INCLUDE_DIR")
    message( FATAL_ERROR "Could not find ${prefix} include!")
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

endif (NOT _LIBFIND_CMAKE_)
