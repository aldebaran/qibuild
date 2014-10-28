## Helper function for the qt5_* qibuild's modules

####
# Find a Qt library
# Usage:
# qt5_flib(QT5_CORE Qt5Core)

function(qt5_flib prefix name)
  find_package(${name})
  set(${prefix}_LIBRARIES ${${name}_LIBRARIES} CACHE INTERNAL "" FORCE)
  set(${prefix}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS} CACHE INTERNAL "" FORCE)
  export_lib(${prefix})
endfunction()
