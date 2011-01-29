##
## Author(s):
##  - Cedric GESTES <cgestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Cedric GESTES
##


include("qibuild/asciidoc")
include("qibuild/doxygen")

function(qi_gen_doc)
  set(_doc_deps)

  cmake_parse_arguments(ARG ""
    "ASCIIDOC_DIR"
    "ASCIIDOC_OPTS;PYGMENTS_OPTS;DOXYFILES"
    ${ARGN})

  if(ARG_ASCIIDOC_DIR)
    qi_gen_asciidoc(${ARG_ASCIIDOC_DIR}
      ASCIIDOC_OPTS ${ARG_ASCIIDOC_OPTS}
      PYGMENTS_OPTS ${ARG_PYGMENTS_OTPS}
    )
    list(APPEND _doc_deps asciidoc)
  endif()

  foreach(_doxyfile ${ARG_DOXYFILES})
    qi_gen_doxygen(doxy_target ${_doxyfile})
    message(STATUS "doxy_target: ${doxy_target}")

    list(APPEND _doc_deps ${doxy_target})
  endforeach()

  add_custom_target(doc)
  add_dependencies(doc ${_doc_deps})
endfunction()
