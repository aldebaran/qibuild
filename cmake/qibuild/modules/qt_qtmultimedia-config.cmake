## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qtutils.cmake")

set(_suffix "QTMULTIMEDIA")
set(_libname "QtMultimedia")

qt_flib(${_suffix} ${_libname})
set(_qtmultimedia_depends "QT_QTCORE;QT_QTGUI")
if(UNIX AND NOT APPLE)
  list(APPEND _qtmultimedia_depends  "ALSALIB")
endif()
qi_persistent_set(QT_QTMULTIMEDIA_DEPENDS ${_qtmultimedia_depends})

export_lib(QT_${_suffix})
set(_ROOT_DIR)
