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

#warning findmodule.*.sdk.in and sdk.cmake use implicit relative path
#between _SDK_LIB and _SDK_CMAKE_MODULES, name could be change, but
#the relative path between each var should remain the same.

qi_set_global(QI_SDK_BIN            "bin"        )
qi_set_global(QI_SDK_LIB            "lib"        )
qi_set_global(QI_SDK_FRAMEWORK      "Frameworks" )
qi_set_global(QI_SDK_INCLUDE        "include"    )
qi_set_global(QI_SDK_SHARE          "share"      )
qi_set_global(QI_SDK_CONF           "etc"        )
qi_set_global(QI_SDK_DOC            "share/doc"  )
qi_set_global(QI_SDK_CMAKE          "share/cmake")
qi_set_global(QI_SDK_CMAKE_MODULES  "cmake")

mark_as_advanced(QI_SDK_BIN
                 QI_SDK_LIB
                 QI_SDK_INCLUDE
                 QI_SDK_SHARE
                 QI_SDK_CONF
                 QI_SDK_DOC
                 QI_SDK_CMAKE
                 QI_SDK_CMAKE_MODULES)
