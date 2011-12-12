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

###############################################
# Auto-generated file.                        #
# Do not edit                                 #
# This file is part of the qiBuild project    #
###############################################

set(BOOTSTRAP_VERSION 6)

#we use t00lchain, when we have a toolchain_file and t00chain_dir is set
if (CMAKE_TOOLCHAIN_FILE AND TOOLCHAIN_DIR)
  set(T001CHAIN_DIR ${TOOLCHAIN_DIR} CACHE PATH "" FORCE)
  include("${T001CHAIN_DIR}/cmake/general.cmake")
  return()
endif()

if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)
  set(QI_T001CHAIN_COMPAT   ON   CACHE INTERNAL "" FORCE)
  set(QI_WARN_DEPRECATED    OFF  CACHE INTERNAL "" FORCE)
  include(${CMAKE_CURRENT_SOURCE_DIR}/qibuild.cmake)
endif()
