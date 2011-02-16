## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild Install
# ================
#
# == General overview ==
# This CMake module provides easy install functions.
# qiBuild generated paths are normalized, these functions help
# create install rules that abstract the final destination
# file hierarchy. Furthermore files are classified by components depending
# on the file type, this make it easy to install only what is needed,
# for example for a runtime install, header and static libs are not needed
# but they are needed for a developement install.
#
# === Files, directories and globbing ===
# Install rules can take directories and globbing rules into account.
# Globbing will not be applied on directories.
#
# \example:install


#! Install application headers.
# On Linux the destination will be <prefix>/include/<subfolder>/
#
# \arg:subfolder The subfolder where headers will be installed
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_header subfolder)
  _qi_install(${ARGN} COMPONENT header DESTINATION ${QI_SDK_INCLUDE}/${subfolder})
endfunction()

#! Install application data.
# On linux the destination will be: <prefix>/share/<subfolder>/
#
# \arg:subfolder The application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_data subfolder)
  _qi_install(${ARGN} COMPONENT data  DESTINATION ${QI_SDK_SHARE}/${subfolder})
endfunction()

#! Install application doc.
# On linux the destination will be: <prefix>/share/doc/<subfolder>/
#
# \arg:subfolder The application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_doc subfolder)
  _qi_install(${ARGN} COMPONENT doc   DESTINATION ${QI_SDK_DOC}/${subfolder})
endfunction()

#! Install application configuration files.
# On linux the destination will be: <prefix>/preferences/<subfolder>/
#
# \arg:subfolder The application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_conf subfolder)
  _qi_install(${ARGN} COMPONENT conf  DESTINATION ${QI_SDK_CONF}/${subfolder})
endfunction()

#! Install Cmake module files. On linux the destination will be <prefix>/share/cmake/<subfolder>/
#
# \arg:subfolder The application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_cmake subfolder)
  _qi_install(${ARGN} COMPONENT cmake DESTINATION ${QI_SDK_CMAKE}/${subfolder})
endfunction()


#! install a target, that could be a program or a library.
#
# \param:SUBFOLDER An optional subfolder
# \argn: A list of target to install
function(qi_install_target)
  cmake_parse_arguments(ARG "" "SUBFOLDER" "" ${ARGN})

  foreach (name ${ARG_UNPARSED_ARGUMENTS})
    install(TARGETS "${name}"
            RUNTIME COMPONENT binary     DESTINATION ${QI_SDK_BIN}/${ARG_SUBFOLDER}
            LIBRARY COMPONENT lib        DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
      PUBLIC_HEADER COMPONENT header     DESTINATION ${QI_SDK_INCLUDE}/${ARG_SUBFOLDER}
           RESOURCE COMPONENT data       DESTINATION ${QI_SDK_SHARE}/${name}/${ARG_SUBFOLDER}
            ARCHIVE COMPONENT static-lib DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER})
  endforeach()
endfunction()

#! install program (mostly script or user provided program). Do not use this function
# to install a library or a program built by your project, prefer using qi_install_target.
#
# \param:SUBFOLDER An optional subfolder
# \argn: A list of programs to install
function(qi_install_program)
  cmake_parse_arguments(ARG "" "SUBFOLDER" "" ${ARGN})
  foreach(name ${ARG_UNPARSED_ARGUMENTS})
    #TODO: what should be the real source here?
    install(PROGRAMS    "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}"
            COMPONENT   binary
            DESTINATION "${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endforeach()
endfunction()

