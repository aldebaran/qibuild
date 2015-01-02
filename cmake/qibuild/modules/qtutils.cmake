## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
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

function(qt_flib _suffix _libname)
  find_program(QT_QMAKE NAMES qmake-qt4 qmake)
  if(QT_QMAKE)
    # Use upstream cmake files
    find_package(Qt4 COMPONENTS ${_libname})
    include("${QT_USE_FILE}")
    # if compoment has not been found, QT_${_suffix}_INCLUDE_DIR will be
    # set to NOT-FOUND, but QT_LIBRARIES will simply not contain the library ...
    if(QT_${_suffix}_INCLUDE_DIR)
      qi_persistent_append_uniq(QT_${_suffix}_INCLUDE_DIRS ${QT_INCLUDE_DIR})
      qi_persistent_append_uniq(QT_${_suffix}_INCLUDE_DIRS ${QT_${_suffix}_INCLUDE_DIR})
      set(QT_${_suffix}_INCLUDE_DIRS ${QT_${_suffix}_INCLUDE_DIRS} PARENT_SCOPE)
    else()
      set(QT_${_suffix}_INCLUDE_DIRS FALSE PARENT_SCOPE)
      set(QT_${_suffix}_PACKAGE_FOUND FALSE PARENT_SCOPE)
    endif()
    qi_persistent_set(QT_${_suffix}_LIBRARIES    "${QT_LIBRARIES}")
    set(QT_${_suffix}_LIBRARIES ${QT_${_suffix}_LIBRARIES} PARENT_SCOPE)
    return()
  endif()


  if(UNIX)
    flib(QT_${_suffix} NAMES "${_libname}" PATH_SUFFIXES qt4)
  else()
    flib(QT_${_suffix} OPTIMIZED NAMES  "${_libname}4"  PATH_SUFFIXES qt4)
    flib(QT_${_suffix} DEBUG     NAMES  "${_libname}d4" PATH_SUFFIXES qt4)
  endif()

  # we don't wand to find the headers in .Frameworks/Headers:
  set(_back ${CMAKE_FIND_FRAMEWORK})
  set(CMAKE_FIND_FRAMEWORK NEVER)
  #we want to be able to #include <QtLib>
  fpath(QT_${_suffix} ${_libname} PATH_SUFFIXES qt4 )

  #we want to be able to #include <QtLib/QtLib>
  fpath(QT_${_suffix} ${_libname} PATH_SUFFIXES ${_libname} qt4/${_libname})
  set(CMAKE_FIND_FRAMEWORK ${_back})
endfunction()
