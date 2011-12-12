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

clean(PYTHON)
# first, use fpath flib to get python from one of our pre-compiled packages
fpath(PYTHON Python.h PATH_SUFFIXES "python2.7" "python2.6")
flib(PYTHON OPTIMIZED NAMES python27 python2.7
                            python26 python2.6
                            Python)
flib(PYTHON DEBUG     NAMES python27_d python2.7
                              python26_d python2.6
                              Python)

if(NOT PYTHON_LIBRARIES OR NOT PYTHON_INCLUDE_DIRS)
  # If it does not work, use upstream cmake code
  # Note: upstream code does NOT work with visual studio on debug
  clean(PYTHON)
  unset(PYTHON_INCLUDE_DIRS)
  unset(PYTHON_INCLUDE_DIRS CACHE)
  find_package(PythonLibs REQUIRED)
  qi_set_global(PYTHON_LIBRARIES ${PYTHON_LIBRARY})
  qi_set_global(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIR})
endif()
export_lib(PYTHON)

