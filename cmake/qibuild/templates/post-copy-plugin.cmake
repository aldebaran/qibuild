## Copyright (C) 2011 Aldebaran Robotics

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the qibuild project    #
###############################################

##
# This file will be called in a post-build step
# from a visual studio project.

# It will copy the plugin DLLS to the correct location.

include(CMakeParseArguments)

set(_input)
string(TOUPPER "${BUILD_TYPE}" _UP_BUILD_TYPE)
set(_input "${LOCATION_${_UP_BUILD_TYPE}}")
message(STATUS "copy: ${_input} -> ${OUTPUT}")
file(COPY ${_input} DESTINATION ${OUTPUT})
