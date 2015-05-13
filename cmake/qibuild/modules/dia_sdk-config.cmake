# finder for the DIA SDK

clean(DIA_SDK)

# Path is c:\Program Files (x86)\Microsoft Visual Studio 10\Common7\Tools,
# we want c:\Program Files (x86)\Microsoft Visual Studio 10\DIA SDK
# We cannot use VSINSTALLDIR because it's not set when using
# 'Visual Studio ...' generators
if(MSVC10)
  set(_comntools_path "$ENV{VS100COMNTOOLS}")
endif()
if(MSVC12)
  set(_comntools_path "$ENV{VS120COMNTOOLS}")
endif()

get_filename_component(_visual_studio_path "${_comntools_path}" DIRECTORY)
get_filename_component(_visual_studio_path "${_visual_studio_path}" DIRECTORY)
set(_dia_sdk_dir "${_visual_studio_path}/DIA SDK")
if(NOT IS_DIRECTORY ${_dia_sdk_dir})
  qi_error("Could not find DIA SDK. (looked in ${_dia_sdk_dir})
Please check your Visual Studio installation")
endif()
set(DIA_SDK_LIBRARIES "${_dia_sdk_dir}/lib/diaguids.lib" CACHE INTERNAL "" FORCE)
set(DIA_SDK_INCLUDE_DIRS "${_dia_sdk_dir}/include" CACHE INTERNAL "" FORCE)
export_lib(DIA_SDK)
