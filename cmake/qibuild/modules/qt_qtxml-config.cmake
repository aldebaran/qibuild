## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qtutils.cmake")

set(_suffix "QTXML")
set(_libame "QtXml")

qt_flib(${_suffix} ${_libame})
export_lib(QT_${_suffix})
set(_ROOT_DIR)
