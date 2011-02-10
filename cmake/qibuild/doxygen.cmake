## Copyright (C) 2011 Aldebaran Robotics

#! Generate doxygen documentation
function(qi_gen_doxygen res doxyfile)
  find_program(DOXYGEN_EXCUTABLE doxygen)
  if(NOT DOXYGEN_EXCUTABLE)
    qi_warning(
    "
      No doxygen doc will be generated: doxygen binary not found
    ")
    return()
  endif()

  # Crate a suitable target name:
  string(REPLACE "/" "_" _name ${doxyfile})
  add_custom_target(doxygen_${_name}
    DEPENDS ${doxyfile}
    COMMAND ${DOXYGEN_EXCUTABLE} ${doxyfile}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  )
  set(${res} doxygen_${_name} PARENT_SCOPE)
endfunction()
