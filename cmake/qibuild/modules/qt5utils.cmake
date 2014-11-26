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
  qi_persistent_set(${prefix}_LIBRARIES ${${name}_LIBRARIES})
  qi_persistent_set(${prefix}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
  set(_define ${prefix}_LIB)
  string(REPLACE QT5 QT _define ${_define})
  qi_persistent_set(${prefix}_DEFINITIONS ${_define})

  export_lib(${prefix})
endfunction()
