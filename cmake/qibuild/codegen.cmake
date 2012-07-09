## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
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
#    qi_generate_src(${_output} SRC ${_input} COMMAND my_script ${_input} > ${_output})
#    qi_create_bin(my_bin ${_output} main.c)
#
# \arg:out the resulting source file
# \group:SRC a group of sources to take as input
# \group:COMMAND the command to run to generate the source file
# \arg:COMMENT a comment to be displayed while generating the source file
#
function(qi_generate_src out)
  cmake_parse_arguments(ARG "" "COMMENT" "SRC;COMMAND" ${ARGN})
  set_source_files_properties(${out} PROPERTIES GENERATED TRUE)
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

