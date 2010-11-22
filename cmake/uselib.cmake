##
## uselib.cmake
## Login : <ctaf@cgestes-de>
## Started on  Tue Oct 27 15:02:10 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

if (NOT _USELIB_CMAKE_)
set(_USELIB_CMAKE_ TRUE)


###########################
# Compute the list of depend target
#
# 1/ is the package needed for this plateform?
# 2/ find the package
# 3/ list and find depend package
# 4/ remove duplicates and return values
#
###########################
function(_use_lib_compute_depends _name OUT_required_dep OUT_optional_dep)
  set(_plateform 1)
  set(_optional 0)
  set(_required_dep)
  set(_optional_dep)

  set(_args ${ARGN})
  foreach(_pa ${ARGN})
    set(_nargs)
    # /1 parse
    use_lib_parse_options(_pkg, _nargs, _plateform, _optional, ${_args})
    set(_args ${_nargs})
    if (_pkg AND _plateform)
      if (_optional)
        set(_optional_dep ${_optional_dep} ${_pkg})
      else (_optional)
        set(_required_dep ${_required_dep} ${_pkg})
      endif (_optional)

      # /2 find
      find(${_pkg} NO_MODULE QUIET)
      if (NOT ${_pkg}_FOUND AND NOT _optional)
        message(FATAL_ERROR "BINLIB: use_lib: Can't find dependency [${_pkg}] for target ${_name}.")
        break()
      endif (NOT ${_pkg}_FOUND AND NOT _optional)

      # /3 find depends
      foreach(_pa2 ${${_pkg}_DEPENDS})
        set(_required_dep ${_required_dep} ${_pa2})
        find(${_pa2} NO_MODULE QUIET)
        if (NOT ${_pa2}_FOUND AND NOT _optional)
          message(FATAL_ERROR "BINLIB: use_lib: Can't find dependency [${_pa2}] for target ${_name} brought by ${_pkg}.")
          break()
        endif (NOT ${_pa2}_FOUND AND NOT _optional)
      endforeach(_pa2 ${_pa2}_DEPENDS)
    endif (_pkg AND _plateform)

  endforeach(_pa ${ARGN})


  # 4/ cleanup then export
  if (_required_dep)
    list(REMOVE_DUPLICATES _required_dep)
  endif (_required_dep)

  if (_optional_dep)
    list(REMOVE_DUPLICATES _optional_dep)
  endif (_optional_dep)

  debug("USELIB: use_lib_depends[${_name}] : Required: ${_required_dep}, Optional: ${_optional_dep}")
  set(${OUT_required_dep} ${_required_dep} PARENT_SCOPE)
  set(${OUT_optional_dep} ${_optional_dep} PARENT_SCOPE)
endfunction(_use_lib_compute_depends)



###########################
#
# make a library available to other project
# wrapper around use_lib to handle static and shared
#
###########################
function(use_lib _name)
  if (${_name}_STATIC_AND_SHARED)
    set(_deps_static)
    foreach(_arg ${ARGN})
      if (${_arg} STREQUAL "LINUX"    OR
          ${_arg} STREQUAL "MACOSX"   OR
          ${_arg} STREQUAL "MAC"      OR
          ${_arg} STREQUAL "REQUIRED" OR
          ${_arg} STREQUAL "OPTIONAL" OR
          ${_arg} STREQUAL "ALL")
        list(APPEND _deps_static "${_arg}")
      else()
        list(APPEND _deps_static "${_arg}-STATIC")
      endif()
    endforeach()
    _use_lib(${_name}-static ${_deps_static})
  endif (${_name}_STATIC_AND_SHARED)
  _use_lib(${_name} ${ARGN})
endfunction(use_lib)

###########################
#
# handle dependencies between targets
#
###########################
function(_use_lib _name)
  set(TMPINC)
  set(TMPLIB)
  set(TMPDEF)
  set(TMPPKG)

  check_is_target(${_name})

  if (${_name}_STAGED)
    error("USELIB: [${_name}] Don't call use_lib on a target after stage_lib. ${_name}, ${${_name}_STAGED}")
  endif (${_name}_STAGED)

  debug("BINLIB: use_lib (${_name}, ${_args})")
  _use_lib_compute_depends(${_name} _required_lib _optional_lib ${ARGN})

  #required
  foreach (_pkg ${_required_lib})
    set(TMPPKG ${TMPPKG} ${_pkg})
    set(TMPINC ${TMPINC} ${${_pkg}_INCLUDE_DIR})
    set(TMPLIB ${TMPLIB} ${${_pkg}_LIBRARIES})
    set(TMPDEF ${TMPDEF} ${${_pkg}_DEFINITIONS})
    set(TMPTARGET ${TMPTARGET} ${${_pkg}_TARGET})
  endforeach (_pkg ${_required_lib})

  #optional
  foreach (_pkg ${_optional_lib})
    #only set them when pkg is found (avoid problem with optional)
    if (${_pkg}_FOUND)
      set(TMPPKG ${TMPPKG} ${_pkg})
      set(TMPINC ${TMPINC} ${${_pkg}_INCLUDE_DIR})
      set(TMPLIB ${TMPLIB} ${${_pkg}_LIBRARIES})
      set(TMPDEF ${TMPDEF} ${${_pkg}_DEFINITIONS})
      set(TMPTARGET ${TMPTARGET} ${${_pkg}_TARGET})
    endif (${_pkg}_FOUND)
  endforeach (_pkg ${_optional_lib})

  verbose("[${_name}] link with ${TMPPKG}")
  debug("BINLIB: use_lib: ${_name} build info:")
  debug("BINLIB: use_lib:  INCLUDE: ${TMPINC}")
  debug("BINLIB: use_lib:  LIBS   : ${TMPLIB}")

  if (TMPTARGET)
    verbose("BINLIB: use_lib: [${_name}] depend on ${TMPTARGET}")
    add_dependencies("${_name}" ${TMPTARGET})
  endif (TMPTARGET)
  if (NOT "${TMPDEF}" STREQUAL "")
    set_directory_properties(PROPERTIES COMPILE_DEFINITIONS "${TMPDEF}")
  endif (NOT "${TMPDEF}" STREQUAL "")
  #store the list of depends in the cache for later use
  if (TMPPKG)
    set(_deps ${TMPPKG} "${${_name}_DEPENDS}")
    if (_deps)
      list(REMOVE_DUPLICATES _deps)
    endif (_deps)
    set(${_name}_DEPENDS ${_deps} CACHE INTERNAL "" FORCE)
  endif (TMPPKG)

  # resolve include paths, they will be de-duplicated later
  set(TMPINC_CLEANED)
  foreach (_inc ${TMPINC})
    get_filename_component(_inc_clean ${_inc} REALPATH)
    list(APPEND TMPINC_CLEANED "${_inc_clean}")
  endforeach (_inc ${TMPINC})
  
  include_directories(${TMPINC_CLEANED})
  target_link_libraries("${_name}" ${TMPLIB})
endfunction(_use_lib _name)


endif (NOT _USELIB_CMAKE_)
