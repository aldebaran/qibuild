##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#! generate cmake install rules for an autotools like project.
message(STATUS "AUTOTOOLS SOURCE FOLDER: @SOURCE_FOLDER@")

function(install_component COMPONENT DEST FILES)
  if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "${COMPONENT}")
    foreach(f ${FILES})
      get_filename_component(_abs_path "${f}" ABSOLUTE)
      if(IS_DIRECTORY ${_abs_path})
        file(INSTALL
             DESTINATION "${CMAKE_INSTALL_PREFIX}/${DEST}"
             TYPE DIRECTORY
             FILES "${f}")
      else()
        file(INSTALL
             DESTINATION "${CMAKE_INSTALL_PREFIX}/${DEST}"
             TYPE FILE
             FILES "${f}")
      endif()
    endforeach()
  endif()
endfunction()

function(install_component_pgm COMPONENT DEST FILES)
  if(NOT CMAKE_INSTALL_COMPONENT OR "${CMAKE_INSTALL_COMPONENT}" STREQUAL "${COMPONENT}")
    foreach(f ${FILES})
      file(INSTALL
           DESTINATION "${CMAKE_INSTALL_PREFIX}/${DEST}"
           TYPE PROGRAM
           FILES "${f}")
    endforeach()
  endif()
endfunction()

file(GLOB _headers "@SOURCE_FOLDER@/include/*")
install_component(header include "${_headers}")

file(GLOB _datas "@SOURCE_FOLDER@/share/*")
install_component(data share "${_datas}")

# #TODO: .lib, .dylib, .dll
file(GLOB _sta_to_install "@SOURCE_FOLDER@/lib/*.a")
install_component_pgm(static-lib lib "${_sta_to_install}")

file(GLOB _dyn_to_install "@SOURCE_FOLDER@/lib/*.so*")
install_component_pgm(lib lib "${_dyn_to_install}")
