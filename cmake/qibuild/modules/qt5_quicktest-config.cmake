## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qt5utils.cmake")

qt5_flib(QT5_QUICKTEST Qt5QuickTest)
qi_persistent_set(QT5_QUICKTEST_DEPENDS QT5_TEST QT5_WIDGETS QT5_CORE)
