##
## gitutils.cmake
##

find(GIT QUIET)

#####################
# Get a nice revision number from a git dir.
#
# Simply call git describe --always --tag and
# return output in ${prefix}_REVISION
#
# You can by-pass this by using the GIT_FORCE_VERSION
# variable.
#####################
function(git_version dir prefix)
  if (DEFINED GIT_FORCE_VERSION)
    set(${prefix}_REVISION ${GIT_FORCE_VERSION} PARENT_SCOPE)
    return()
  endif (DEFINED GIT_FORCE_VERSION)

  set(_out)
  if(GIT_EXECUTABLE)
    execute_process(
      COMMAND           ${GIT_EXECUTABLE} describe --always --tag
      WORKING_DIRECTORY ${dir}
      RESULT_VARIABLE   _result
      OUTPUT_VARIABLE   _out
      ERROR_VARIABLE    _error
      OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(${_result} EQUAL 0)
      set(_rev "${_out}")
    endif(${_result} EQUAL 0)
  endif(GIT_EXECUTABLE)

  #always set a revision, fallback to the perfect revision, the one that just work!
  if (NOT _rev)
    set(_rev "42-nogit")
  endif (NOT _rev)



  # git describe --always --tags will return "tags/v1.2.45", for instance.
 # Remove the tags/ part:
  string(REGEX REPLACE "tags/" "" _result ${_rev})
  set(${prefix}_REVISION "${_result}" PARENT_SCOPE)
endfunction()


#################
# Extract a short version from a full
# git_version call.
# Given a revision 1.4.14-rc2-42-ae452 (which changes at every commit),
# set revision result 1.4.14-rc2.
# When used with generate_revision_header, this is useful to avoid re-compiliation
# of everything after each commit, but assures that we will re-compile when a new tag
# is put.
####################
function(git_short_version _res _version)
  string(REGEX MATCH "v?([0-9]*\\.[0-9]*)\\.([0-9]*(-rc[0-9]+)?)[\\.\\-]?(.*)" _tmp ${_version})
  if(_tmp)
    set(${_res} "${CMAKE_MATCH_1}.${CMAKE_MATCH_2}" PARENT_SCOPE)
  else()
    set(${_res} ${_version} PARENT_SCOPE)
  endif()
endfunction()

