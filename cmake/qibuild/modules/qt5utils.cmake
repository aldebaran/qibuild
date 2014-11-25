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
      get_target_property(_imported_lib_debug ${_lib} IMPORTED_IMPLIB_DEBUG)
      get_target_property(_imported_lib_release ${_lib} IMPORTED_IMPLIB_RELEASE)
      list(APPEND ${prefix}_LIBRARIES
        optimized ${_imported_lib_release}
        debug ${_imported_lib_debug}
      )
    else()
      get_target_property(_lib_loc ${_lib} LOCATION)
      list(APPEND ${prefix}_LIBRARIES ${_lib_loc})
    endif()
  endforeach()
  set(${prefix}_LIBRARIES ${${prefix}_LIBRARIES} CACHE INTERNAL "" FORCE)
  set(${prefix}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS} CACHE INTERNAL "" FORCE)
  set(_define ${prefix}_lib)
  string(REPLACE QT5 QT _define ${_define})
  set(${prefix}_DEFINITIONS ${_define} CACHE INTERNAL "" FORCE)

  export_lib(${prefix})
endfunction()
