## Helper function for the qt5_* qibuild's modules

####
# Find a Qt library
# Usage:
# qt5_flib(QT5_CORE Qt5Core)

function(qt5_flib prefix name)
  set(${prefix}_LIBRARIES)
  # upstream uses Qt5::Core notation but we need to dereference this
  # because we won't be calling find_package() again
  find_package(${name})
  foreach(_lib ${${name}_LIBRARIES})
    if(WIN32)
      get_target_property(_lib_loc_debug ${_lib} LOCATION_DEBUG)
      get_target_property(_lib_loc_release ${_lib} LOCATION_RELEASE)
      list(APPEND ${prefix}_LIBRARIES
      debug "${_lib_loc_debug}"
      optimized "${_lib_loc_release}")
    else()
      get_target_property(_lib_loc ${_lib} LOCATION)
      list(APPEND ${prefix}_LIBRARIES ${_lib_loc})
    endif()
  endforeach()
  set(${prefix}_LIBRARIES ${${prefix}_LIBRARIES} CACHE INTERNAL "" FORCE)
  set(${prefix}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS} CACHE INTERNAL "" FORCE)

  export_lib(${prefix})
endfunction()
