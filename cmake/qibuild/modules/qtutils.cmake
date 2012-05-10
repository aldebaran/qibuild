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

include(qibuild/modules/qt-tools)

function(qt_flib _suffix _libame)
  if(QT_USE_QMAKE)
    # Use upstream cmake files
    find_package(Qt4 COMPONENTS ${_libname} REQUIRED)
    include("${QT_USE_FILE}")
    # if compoment has not been found, QT_${_suffix}_INCLUDE_DIR will be
    # set to NOT-FOUND, but QT_LIBRARIES will simply not contain the library ...
    if(QT_${_suffix}_INCLUDE_DIR)
      qi_append_uniq_global(QT_${_suffix}_INCLUDE_DIRS ${QT_INCLUDE_DIR})
      qi_append_uniq_global(QT_${_suffix}_INCLUDE_DIRS ${QT_${_suffix}_INCLUDE_DIR})
      set(QT_${_suffix}_INCLUDE_DIRS ${QT_${_suffix}_INCLUDE_DIRS} PARENT_SCOPE)
    else()
      set(QT_${_suffix}_INCLUDE_DIRS FALSE PARENT_SCOPE)
    endif()
    qi_append_uniq_global(QT_${_suffix}_LIBRARIES    "${QT_LIBRARIES}")
    set(QT_${_suffix}_LIBRARIES ${QT_${_suffix}_LIBRARIES} PARENT_SCOPE)
    return()
  endif()


  flib(QT_${_suffix} OPTIMIZED NAMES "${_libame}" "${_libame}4"  PATH_SUFFIXES qt4)
  flib(QT_${_suffix} DEBUG     NAMES "${_libame}" "${_libame}d4" PATH_SUFFIXES qt4)

  #we want to be able to #include <QtLib>
  fpath(QT_${_suffix} ${_libame} PATH_SUFFIXES qt4 )

  #we want to be able to #include <QtLib/QtLib>
  fpath(QT_${_suffix} ${_libame} PATH_SUFFIXES ${_libame} qt4/${_libame})
endfunction()
