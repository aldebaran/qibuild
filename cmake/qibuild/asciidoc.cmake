##
## Copyright (C) 2008, 2010, 2011 Aldebaran Robotics
##

#! QiBuild Asciidoc
# =================

#!
# This is a set of tools to generate asciidoc documentation with examples.
# It requires asccidoc >= 8.6.3 and python-pygments
#
# For instance, assuming you have a doc/ directory looking like:
#
#  doc
#  |__ index.txt
#  |__ chapter_one
#        |__ one.txt
#        |__ two.txt
#  |__ examples
#      |__ foo
#          |__ CMakeLists.txt
#          |__ foo.cpp
#  |__ css
#      |__ doc.css

# This will enable you to have:
#
#  build-doc
#  |__ index.html
#  |__ chapter_one
#        |__ one.html
#        |__ two.html
#  |__ examples
#      |__ foo
#          |__ CMakeLists.txt.html
#          |__ foo.cpp.html
# |__ css
#     |__ doc.css
#
# Where:
#  - A nice syntax-higlighted .html is generated for each source code file.
#  - A .html file is generated for each .txt found
#  - File hierarchy is presevered, so that using relative links always work.

#! Generate asciidoc from a documentation folder
# \arg: doc_folder the directory where to find the documentation
# \group:ASCIIDOC_OPTS flags to be passed to the asciidoc executable
# A target called "asciidoc" is created
function(qi_gen_asciidoc doc_folder)
  find_program(ASCIIDOC_EXCUTABLE asciidoc)
  if(NOT ASCIIDOC_EXCUTABLE)
    qi_warning(
    "
      No asciidoc will be generated: asciidoc binary not found
    ")
    return()
  endif()
  find_program(PYGMENTIZE_EXECUTABLE pygmentize)
  if(NOT PYGMENTIZE_EXECUTABLE)
    qi_warning(
    "
      No asciidoc will be generated: pygmentize binary not found
      Try installing python-pygments
    ")
    return()
  endif()

  set(_outputs)

  cmake_parse_arguments(ARG "" ""
    "ASCIIDOC_OPTS;PYGMENTS_OPTS" ${ARGN})
  set(_asciidoc_opts  ${ARG_ASCIIDOC_OPTS})
  set(_pygments_opts  ${ARG_PYGMENTS_OTPS})

  file(GLOB_RECURSE _inputs ${doc_folder}/*)
  # Iterate on files in the directory, generating rules
  # and adding every files as a dependency to the "doc" target
  foreach(_input ${_inputs})
    _qi_is_asciidoc(_asciidoc ${_input})
    _qi_is_source_code(_source_code ${_input})
    if(${_asciidoc})
      _qi_add_asciidoc_rule(_output
        ${doc_folder}
        ${_input}
        ${_asciidoc_opts})
    elseif(${_source_code})
      _qi_add_source_code_rule(_output
        ${doc_folder}
        ${_input}
        ${_pygments_opts})
    else()
      _qi_add_copy_rule(_output ${doc_folder} ${_input})
    endif()
    list(APPEND _outputs ${_output})
  endforeach()

  add_custom_target(asciidoc_${doc_folder}
    DEPENDS ${_outputs}
  )
endfunction()


# Guess if a file is an asciidoc file:
function(_qi_is_asciidoc res filename)
  get_filename_component(_ext ${filename} EXT)
  get_filename_component(_name ${filename} NAME)

  if(NOT _ext)
    set(${res} FALSE PARENT_SCOPE)
    return()
  endif()

  if(NOT ${_ext} STREQUAL ".txt")
    set(${res} FALSE PARENT_SCOPE)
    return()
  endif()

  if(${_name} STREQUAL "CMakeLists.txt")
    set(${res} FALSE PARENT_SCOPE)
    return()
  endif()

  set(${res} TRUE PARENT_SCOPE)
endfunction()



# Guess if filename is source code example
function(_qi_is_source_code res filename)
  get_filename_component(_ext ${filename} EXT)
  get_filename_component(_name ${filename} NAME)

  if(${_name} STREQUAL "CMakeLists.txt")
    set(${res} TRUE PARENT_SCOPE)
    return()
  endif()

  if(NOT _ext)
    set(${res} FALSE PARENT_SCOPE)
    return()
  endif()

  set(_knwown_exts .cpp .h .py .cmake)
  foreach(_knwown_ext ${_knwown_exts})
    if(${_ext} STREQUAL ${_knwown_ext})
      set(${res} TRUE PARENT_SCOPE)
      return()
    endif()
  endforeach()
  set(${res} FALSE PARENT_SCOPE)
endfunction()

function(_qi_add_asciidoc_rule output doc_folder input)
  file(RELATIVE_PATH _input_re ${CMAKE_SOURCE_DIR}/${doc_folder} ${input})
  string(REPLACE ".txt" ".html" _output_re ${_input_re})
  set(_output ${CMAKE_SOURCE_DIR}/build-doc/${doc_folder}/${_output_re})
  # Make sure output directory exists:
  get_filename_component(_output_path ${_output} PATH)
  file(MAKE_DIRECTORY ${_output_path})

  add_custom_command(
    OUTPUT ${_output}
    COMMAND ${ASCIIDOC_EXCUTABLE}
            ${ARGN}
            "--out-file=${_output}"
            "${_input}"
    DEPENDS ${_input}
  )

  set(${output} ${_output} PARENT_SCOPE)
endfunction()


function(_qi_add_source_code_rule output doc_folder input)
  file(RELATIVE_PATH _input_re ${CMAKE_SOURCE_DIR}/${doc_folder} ${input})
  set(_output ${CMAKE_SOURCE_DIR}/build-doc/${doc_folder}/${_input_re}.html)
  # Make sure output directory exists:
  get_filename_component(_output_path ${_output} PATH)
  file(MAKE_DIRECTORY ${_output_path})
  set(_pygments_opts ${ARGN})
  # Little help for pygmentize:
  get_filename_component(_name ${_input_re} NAME)
  if (${_name} STREQUAL "CMakeLists.txt")
    list(APPEND _pygments_opts -l cmake)
  endif()
  add_custom_command(
    OUTPUT ${_output}

    COMMAND ${PYGMENTIZE_EXECUTABLE}
      "-o"  "${_output}"
      "-O" full
      ${_pygments_opts}
      "${_input}"

    DEPENDS ${_input}
  )
  set(${output} ${_output} PARENT_SCOPE)
endfunction()


function(_qi_add_copy_rule output doc_folder input)
  file(RELATIVE_PATH _input_re ${CMAKE_SOURCE_DIR}/${doc_folder} ${input})
  set(_output ${CMAKE_SOURCE_DIR}/build-doc/${doc_folder}/${_input_re})
  add_custom_command(
    OUTPUT ${_output}
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
      ${_input}
      ${_output}
    DEPENDS ${_input}
  )
  set(${output} ${_output} PARENT_SCOPE)
endfunction()
