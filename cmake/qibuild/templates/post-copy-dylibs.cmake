##
## Copyright (C) 2010 Aldebaran Robotics
##
####

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the qibuild project    #
###############################################

##
# This file will be called in a post-build step
# if we are building on mac.

# It will copy all the required .dylib in the build/sdk/lib/
# folder

# PROJECT : upper-case name of the target beeing built.
#          (${PROJECT}_DEPENDS must exist in the CMake cache)

set(_libs)

foreach(_dep ${${PROJECT}_DEPENDS})
  string(TOUPPER ${_dep} _U_dep)
  list(APPEND _libs ${${_U_dep}_LIBRARIES})
  list(APPEND _libs ${${_U_dep}_LIBRARY})
endforeach()


set(_in_dylibs)

foreach(_lib ${_libs})
  if(${_lib} MATCHES ".*\\.dylib")
    message(STATUS "_lib: ${_lib}")
    list(APPEND _in_dylibs ${_lib})
  endif()
endforeach()

file(COPY ${_in_dylibs} DESTINATION ${CMAKE_BINARY_DIR}/sdk/lib)
