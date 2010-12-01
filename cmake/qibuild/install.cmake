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
