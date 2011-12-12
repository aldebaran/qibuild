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

if(WIN32)
    add_definitions(" -DWIN32_LEAN_AND_MEAN ")
    add_definitions(" -D_CRT_SECURE_NO_DEPRECATE ")
endif()

option(DISABLE_PRECOMPILED_HEADERS "If ON, the macro add_msvc_precompiled_header will be disabled (ON or OFF)" ON)

################################################################################
# Object: Adds a cpp to your project that references a header containing
# includes of external headers that never change. By including these in
# a precompiled header, re-compile and compile times decrease dramtically.
# Each cpp in sources_var will have a dependence added to this header, and
# will effectively include the result of this header as its first include.

# Your cpp:
# #include yourmodule_pch.h

# Your h:
# #ifndef YOURMODULE_PCH_H
#  #define YOURMODULE_PCH_H
#  if _MSC_VER > 1000
#  pragma message( "Using pre-compiled headers\n" )
#
#  // Std library stuff
#  #include <vector>
#  [ other includes ...]
#
# #endif // _MSC_VER
# #endif // YOURMODULE_PCH_H
#
################################################################################
macro(add_msvc_precompiled_header precompiled_header precompiled_source sources_var)

  if(NOT DISABLE_PRECOMPILED_HEADERS)
      # Only do this for Visual Studio
      if(MSVC)
        # Create a name based on the project output
        get_filename_component(precompiled_basename ${precompiled_header} NAME_WE)
        set(precompiled_binary "\$(IntDir)/${precompiled_basename}.pch")

        # Decipher the sources list from the name of the arg
        SET(sources ${${sources_var}})

        # Tell the compiler about the cpp which will create the precompiled header
        set_source_files_properties(
            ${precompiled_source}
            PROPERTIES COMPILE_FLAGS "/Yc\"${precompiled_header}\"  /Fp\"${precompiled_binary}\""
            OBJECT_OUTPUTS "${precompiled_binary}"
        )

        # force this precompiled header into cpp files, and make sure they depend
        foreach( src_file ${sources} )
            get_filename_component(src_extension ${src_file} EXT)
            if ( ${src_extension} STREQUAL ".cpp" )
                set_source_files_properties(
                    ${src_file}
                    PROPERTIES
                    COMPILE_FLAGS "/Yu\"${precompiled_header}\" /FI\"${precompiled_header}\" /Fp\"${precompiled_binary}\""
                    OBJECT_DEPENDS "${precompiled_binary}"
                )
            endif ()
        endforeach()

        # Add precompiled cpp to sources
        list(APPEND ${sources_var} ${precompiled_source})

      endif()
  endif()
endmacro()
