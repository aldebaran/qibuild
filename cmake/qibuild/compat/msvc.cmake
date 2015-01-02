## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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
