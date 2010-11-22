##
## Author(s):
##  - Cedric GESTES <cgestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Cedric GESTES
##

find(ASCIIDOC QUIET)
find(DOXYGEN QUIET)

#The doc target will generate all the documentation, including asciidoc and doxygen.

####################################################################
#
# compile a set of asciidoc documentation
#
####################################################################
function(create_asciidoc subfoldername)
  if(ASCIIDOC_FOUND)
    if (NOT TARGET "doc")
      add_custom_target("doc")
    endif (NOT TARGET "doc")

    make_directory("${SDK_DIR}/share/doc/${subfoldername}/")
    foreach(_file ${ARGN})
      get_filename_component(_file_we ${_file} NAME_WE)
      set(_in   "${_file_we}-asciidoc")
      set(_out  "${SDK_DIR}/${_SDK_DOC}/${subfoldername}/${_file_we}.html")
      #set(_rout "${SDK_DIR}/share/doc/${subfoldername}/${_file_we}.html")
      set(_fin  "${CMAKE_CURRENT_SOURCE_DIR}/${_file}")

      debug("Adding asciidoc: ${_out} : ${_in}")

      install(FILES "${_out}" COMPONENT doc DESTINATION "${_SDK_DOC}/${subfoldername}/")

      # way to go, but asciidoc leave the file in the filesystem even on error
      # So when an error occur, the next time you try to build, cmake think the previous
      # build is ok (the erronous file is at the right place) and continue building
      # # debug("DOC: file: ${_file}, input: ${_fin}, output: ${_out}")
      # add_custom_command(
      #         OUTPUT "${_out}"
      #         COMMAND "${ASCIIDOC_EXECUTABLE}" -a toc -o "${_out}" "${_fin}"
      #         DEPENDS "${_fin}"
      #         COMMENT "Asciidoc ${_in}"
      #         )
      #       add_custom
      # #a target is needed to have depends (the doc taret wont work otherwize)
      # add_custom_target("${_in}" DEPENDS "${_out}")

      #ATM always rebuild the doc... or find a way to correct asciidoc
      add_custom_target("${_in}"
           #             DEPENDS "${_out}"
                        COMMAND "${ASCIIDOC_EXECUTABLE}" -a toc -o "${_out}" "${_fin}"
                        COMMENT "Asciidoc ${_in}")

      add_dependencies("doc" "${_in}")
    endforeach(_file)
  else(ASCIIDOC_FOUND)
    message(STATUS "###### WARNING ######")
    message(STATUS "No asciidoc will be generated: asciidoc binary not found")
    message(STATUS "Please install asciidoc")
    message(STATUS "###### WARNING ######")
  endif(ASCIIDOC_FOUND)
endfunction(create_asciidoc foldername)


####################################################################
#
# generate doxygen
#
####################################################################
function(create_doxygen)

  if (DOXYGEN_EXECUTABLE)
    if (NOT TARGET "doc")
      add_custom_target("doc")
    endif (NOT TARGET "doc")

    #find a unique targetname
    #how to we do n+n? ok we wont... n + n = nn no?
    set(_doxygen_target "doxygen")
    while(TARGET "${_doxygen_target}")
      set(_doxygen_target "${_doxygen_target}n")
    endwhile()

    message(STATUS "Doxygen(${_doxygen_target}): ${ARGV0}")
    add_custom_target("${_doxygen_target}" COMMAND ${DOXYGEN_EXECUTABLE} ${ARGV0} WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
    add_dependencies("doc" "${_doxygen_target}")
  endif()
endfunction(create_doxygen)
