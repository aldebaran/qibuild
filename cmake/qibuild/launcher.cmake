##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#!
#
# Create a trampoline for an executable.
#  ( and the install rule that goes with it)
# Note: this trampoline will only work when installed!
#
# Usage:
# gen_trampoline(_binary_name _trampoline_name)
#TODO: DOC
#FIXME: is this really necessary?
function(qi_create_launcher _binary_name _trampo_name)
  configure_file("${T001CHAIN_DIR}/cmake/templates/trampoline_${TARGET_ARCH}.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}"
                  @ONLY)
  install(PROGRAMS
    "${CMAKE_CURRENT_BINARY_DIR}/${_trampo_name}"
    COMPONENT binary
    DESTINATION
    ".")
endfunction()
