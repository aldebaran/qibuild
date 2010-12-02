####
# Useful things for qt.
#

# Uncomment this to use Qt from system
#set(QT_IN_SYSTEM SYSTEM CACHE INTERNAL "" FORCE)
set(QT_IN_SYSTEM "" CACHE INTERNAL "" FORCE)


####
# Find a Qt library
# Usage:
# qt_flib(QTCORE "QtCore")
# will look for libQtCore.so, and Qtcore4{d}.dll,
# and include/QtCore
#
function(qt_flib _suffix _libame)
   flib(QT_${_suffix} OPTIMIZED
    NAMES
      "${_libame}"
      "${_libame}4" ${QT_IN_SYSTEM})


   flib(QT_${_suffix} DEBUG
    NAMES
      "${_libame}"
      "${_libame}d4" ${QT_IN_SYSTEM})

   #we want to be able to #include <QtLib>
   fpath(QT_${_suffix} ${_libame} ${QT_IN_SYSTEM})

   #we want to be able to #include <QtLib/QtLib>
   fpath(QT_${_suffix} ${_libame}
         PATH_SUFFIXES ${_libame} ${QT_IN_SYSTEM})

endfunction()
