## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

####
# Find a Qt library
# Usage:
# qt_flib(QTCORE "QtCore")
# will look for libQtCore.so, and Qtcore4{d}.dll,
# and include/QtCore
#
function(qt_flib _suffix _libame)
  find_program(QT_QMAKE qmake)
  if(QT_QMAKE)
    # Use upstream cmake files
    find_package(Qt4 COMPONENTS ${_libname} REQUIRED)
    include("${QT_USE_FILE}")
    set(QT_${_suffix}_INCLUDE_DIRS ${QT_INCLUDE_DIR} PARENT_SCOPE)
    set(QT_${_suffix}_LIBRARIES    ${QT_LIBRARIES}   PARENT_SCOPE)
    return()
  endif()

  flib(QT_${_suffix} OPTIMIZED NAMES "${_libame}" "${_libame}4"  PATH_SUFFIXES qt4)
  flib(QT_${_suffix} DEBUG     NAMES "${_libame}" "${_libame}d4" PATH_SUFFIXES qt4)

  #we want to be able to #include <QtLib>
  fpath(QT_${_suffix} ${_libame} PATH_SUFFIXES qt4 )

  #we want to be able to #include <QtLib/QtLib>
  fpath(QT_${_suffix} ${_libame} PATH_SUFFIXES ${_libame} qt4/${_libame})
endfunction()
