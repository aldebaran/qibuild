## Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qt5utils.cmake")

qt5_flib(QT5_QUICKCONTROLS2 Qt5QuickControls2)
qi_persistent_set(QT5_QUICKCONTROLS2_DEPENDS QT5_GUI QT5_QML QT5_QUICK)
