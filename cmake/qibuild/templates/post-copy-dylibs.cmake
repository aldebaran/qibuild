## Copyright (C) 2011 Aldebaran Robotics

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

# target is a variable set by the caller.

string(TOUPPER ${target} _U_target)

set(_libs)

foreach(_dep ${${_U_target}_DEPENDS})
  string(TOUPPER ${_dep} _U_dep)
  list(APPEND _libs ${${_U_dep}_LIBRARIES})
  list(APPEND _libs ${${_U_dep}_LIBRARY})
endforeach()


set(_in_dylibs)

foreach(_lib ${_libs})
  if(${_lib} MATCHES ".*\\.dylib")
    get_filename_component(_abs ${_lib} REALPATH)
    list(APPEND _in_dylibs ${_abs})
  endif()
endforeach()

if(_in_dylibs)
  list(REMOVE_DUPLICATES _in_dylibs)
endif()

if($ENV{VERBOSE})
  message(STATUS "copying ${_in_dylibs} -> ${QI_SDK_DIR}/${QI_SDK_LIB}")
endif()

file(COPY ${_in_dylibs} DESTINATION ${QI_SDK_DIR}/${QI_SDK_LIB})
