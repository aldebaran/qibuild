##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

#! QiBuild Install
# ================
# Cedric GESTES <gestes@aldebaran-robotics.com>
#
# == General overview ==
# This cmake module provide easy install functions.
# QiBuild generated path are normalized, thoses functions help
# creating install rules that abstract the final destination
# file hierarchy. Furthermore files are classified by components depending
# on the file type, this make it easy to install only what is needed,
# for example for a runtime install, header and static libs are not needed
# but they are needed for a developement install.
#
# === Files, directories and globbing ===
# install rules can take directories and globbing rules into account.
# globbing will not be applied on directories.
#
# \example:install


#! Install application headers.
# Under Linux the destination will be <prefix>/include/<subfolder>/
#
# \arg:subfolder the subfolder where headers will be installed
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_header subfolder)
  _qi_install(${ARGN} COMPONENT header DESTINATION ${QI_SDK_INCLUDE}/${subfolder})
endfunction()

#! Install application data.
# Under linux the destination will be: <prefix>/share/<subfolder>/
#
# \arg:subfolder the application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_data subfolder)
  _qi_install(${ARGN} COMPONENT data  DESTINATION ${QI_SDK_SHARE}/${subfolder})
endfunction()

#! Install application doc.
# Under linux the destination will be: <prefix>/share/doc/<subfolder>/
#
# \arg:subfolder the application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_doc subfolder)
  _qi_install(${ARGN} COMPONENT doc   DESTINATION ${QI_SDK_DOC}/${subfolder})
endfunction()

#! Install application configuration files.
# Under linux the destination will be: <prefix>/preferences/<subfolder>/
#
# \arg:subfolder the application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_conf subfolder)
  _qi_install(${ARGN} COMPONENT conf  DESTINATION ${QI_SDK_CONF}/${subfolder})
endfunction()

#! Install Cmake module files. Under linux the destination will be <prefix>/share/cmake/<subfolder>/
#
# \arg:subfolder the application name
# \argn: list of files. Directories and globs on files are accepted.
function(qi_install_cmake subfolder)
  _qi_install(${ARGN} COMPONENT cmake DESTINATION ${QI_SDK_CMAKE}/${subfolder})
endfunction()


#! install a target, that could be a program or a library.
#
# \param:SUBFOLDER an optional subfolder
# \argn: a list of target to install
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
# to install library or program built by your project, prefer using qi_install_target.
#
# \param:SUBFOLDER an optional subfolder
# \argn: a list of program to install
function(qi_install_program)
  cmake_parse_arguments(ARG "" "SUBFOLDER" "" ${ARGN})
  foreach(name ${ARG_UNPARSED_ARGUMENTS})
    #TODO: what should be the real source here?
    install(PROGRAMS    "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}"
            COMPONENT   binary
            DESTINATION "${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endforeach()
endfunction()

