## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qtutils.cmake")

set(_suffix "QTDBUS")
set(_libame "QtDBus")

qt_flib(${_suffix} ${_libame})
if(UNIX AND NOT APPLE)
  qi_persistent_set(QT_QTDBUS_DEPENDS "DBUS-1")
  qi_persistent_set(QT_QTDBUS_DEPENDS "QTCORE")
  qi_persistent_set(QT_QTDBUS_DEPENDS "QTXML")
  qi_persistent_set(QT_QTDBUS_DEPENDS "GLIB2")
endif()

export_lib(QT_${_suffix})
set(_ROOT_DIR)
