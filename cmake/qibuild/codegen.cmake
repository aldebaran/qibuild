## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


#! Source code generation
# =======================

#! Generate a source file
#
# Example of use: ::
#
#    set(_input ${CMAKE_CURRENT_SOURCE_DIR}/input.data)
#    set(_output ${CMAKE_CURRENT_BINARY_DIR}/generated.c)
#    qi_generate_src(${_output} SRC ${_input} COMMAND my_script ${_input} -o ${_output})
#    qi_create_bin(my_bin ${_output} main.c)
#
# Note that the base dir of the output will automatically be created, so
# you do not have to worry about it in your script.
#
# \arg:out the generated files in a list
# \group:SRC a group of sources to take as input
# \group:COMMAND the command to run to generate the files
# \arg:COMMENT a comment to be displayed while generating the source file
function(qi_generate_src)
  cmake_parse_arguments(ARG "" "COMMENT" "SRC;COMMAND" ${ARGN})
  set(out ${ARG_UNPARSED_ARGUMENTS})
  foreach(_out_file ${out})
    set_source_files_properties(${_out_file}
        PROPERTIES GENERATED TRUE)
    get_filename_component(_out_dir ${_out_file} PATH)
    file(MAKE_DIRECTORY ${_out_dir})
  endforeach()
  set(_comment "Generating ${out} ....")
  if(ARG_COMMENT)
    set(_comment ${ARG_COMMENT})
  endif()
  list(GET ARG_COMMAND 0 _cmd)
  list(REMOVE_AT ARG_COMMAND 0)
  add_custom_command(OUTPUT ${out}
                     COMMENT "${_comment}"
                     COMMAND ${_cmd}
                     ARGS ${ARG_COMMAND}
                     DEPENDS ${ARG_SRC}
  )
endfunction()


#! Generate a header
#
# Example of use: ::
#
#   set(_input ${CMAKE_CURRENT_SOURCE_DIR}/input.data)
#   set(_generated_h ${CMAKE_CURRENT_BINARY_DIR}/generated.h)
#   qi_generate_header(${_generated_h} SRC ${_input}
#    COMMAND my_script ${_input} -o ${_generated_h})
#   qi_create_bin(foo ${_generated_h} main.c)
#   qi_install_header(${_generated_h})
#
# Notes:
#  * the base dir of the header will automatically be created, so
#    you do not have to worry about it in your script.
#  * ``include_directories()`` will be called with the directory where
#    the header is generated.
#
#
# \arg:out the resulting source file
# \group:SRC a group of sources to take as input
# \group:COMMAND the command to run to generate the source file
# \arg:COMMENT a comment to be displayed while generating the source file
function(qi_generate_header out)
  get_filename_component(_header_dir ${out} PATH)
  include_directories(${_header_dir})
  qi_generate_src(${out} ${ARGN})
endfunction()

