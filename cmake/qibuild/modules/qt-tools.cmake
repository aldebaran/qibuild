## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qt-tools-common.cmake")

# Hack here: we cannot integrate qmake in the
# qt packages in the toolchains, because qmake will report
# a path that probably does not exist, so we instead
# look for moc and uic, and the copy-paste the macros from
# QT_USE_FILE ...

find_program(QT_MOC_EXECUTABLE NAMES moc-qt4 moc)
find_program(QT_UIC_EXECUTABLE NAMES uic-qt4 uic)
find_program(QT_RCC_EXECUTABLE NAMES rcc-qt4 rcc)
include("${_ROOT_DIR}/Qt4Macros.cmake")

#! Generate qt.conf. Assumes qi_use_lib(... QT_QTCORE) has been called
#
function(qi_generate_qt_conf)
  # First, find qt and generate qt.conf
  # containing paths in the toolchain
  if(DEFINED QT_PLUGINS_PATH)
    set(_plugins_path "${QT_PLUGINS_PATH}")
  else()
    list(GET QT_QTCORE_LIBRARIES 0 _lib)
    if("${_lib}" STREQUAL "debug"
        OR "${_lib}" STREQUAL "optimized"
        OR "${_lib}" STREQUAL "general")
      list(GET QT_QTCORE_LIBRARIES 1 _lib)
    endif()

    get_filename_component(_lib_path ${_lib} PATH)
    set(_plugins_path ${_lib_path}/qt4/plugins)
  endif()

  file(WRITE "${QI_SDK_DIR}/${QI_SDK_BIN}/qt.conf"
"[Paths]
Plugins = ${_plugins_path}
")

  # Then, generate and install a qt.conf
  # containing relative paths
  if(APPLE)
    set(_relative_plugins_path "../../lib/qt4/plugins")
  else()
    set(_relative_plugins_path "../lib/qt4/plugins")
  endif()
  file(WRITE "${CMAKE_BINARY_DIR}/qt.conf"
"[Paths]
Plugins = ${_relative_plugins_path}
")
  install(FILES "${CMAKE_BINARY_DIR}/qt.conf" DESTINATION bin COMPONENT runtime)

endfunction()
