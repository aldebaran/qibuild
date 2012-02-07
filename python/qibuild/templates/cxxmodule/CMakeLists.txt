cmake_minimum_required(VERSION 2.8)

## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
project(@project_name@)

# You need this to find the QiBuild CMake framework
include("qibuild.cmake")


# Create a list of source files
set(_remote_srcs
    @module_name@.cpp
    @module_name@.h
    main.cpp)

# Create a executable named @project_name@_broker
# with the source file: main.cpp
qi_create_bin(@project_name@_broker ${_remote_srcs})

# Create a list of source files
set(_dll_srcs
    @module_name@.cpp
    @module_name@.h
    dllmain.cpp)

# Create a plugin, that is a shared library, and make
# sure it is built in lib/naoqi
qi_create_lib(@project_name@ SHARED ${_dll_srcs} SUBFOLDER naoqi)


# Tell CMake that myproject depends on ALCOMMON
# This will set the libraries to link myproject with
# the include paths, and so on
qi_use_lib(@project_name@_broker ALCOMMON)
qi_use_lib(@project_name@ ALCOMMON BOOST)



# Add a simple test:

# Define _test_srcs.
# If you add any sources for your module,
# Please add here.
set(_test_srcs
    @module_name@.cpp
    @module_name@.h
    test.cpp)

# If you want to use simple test,

# Create Test Project.
# CAUTION
# please uncomment the following lines.

#enable_testing()
#qi_create_test(test_@project_name@ ${_test_srcs})
#qi_use_lib(test_@project_name@ ALCOMMON)


