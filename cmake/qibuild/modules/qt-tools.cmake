## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Hack here: we cannot integrate qmake in the
# qt packages in the toolchains, because qmake will report
# a path that probably does not exists, so we instead
# look for moc and uic, and the copy-paste the macros from
# QT_USE_FILE ...

# Note: when cross-compiling, you should set QT_USE_QMAKE
# to false so that we do not use qmake from the system.

if(NOT DEFINED QT_USE_QMAKE)
  find_program(QT_QMAKE NAMES qmake-qt4 qmake)
  if(QT_QMAKE)
    set(QT_USE_QMAKE TRUE CACHE INTERNAL "" FORCE)
  else()
    set(QT_USE_QMAKE FALSE CACHE INTERNAL "" FORCE)
  endif()
endif()

if(QT_USE_QMAKE)
  # Use upstream cmake files:
  find_package(Qt4 COMPONENTS "")
  include(Qt4Macros)
else()
  # Using a qt package from a desktop toolchain:
  # look for moc, uic and rcc in the package before
  # including Qt4Macros
  find_program(QT_MOC_EXECUTABLE NAMES moc-qt4 moc)
  find_program(QT_UIC_EXECUTABLE NAMES uic-qt4 uic)
  find_program(QT_RCC_EXECUTABLE NAMES rcc-qt4 rcc)
  include(Qt4Macros)
endif()


#! Generate qt.conf. Assumes qi_use_lib(... QT_QTCORE) has been called
#
function(qi_generate_qt_conf)
  # First, find qt and generate qt.conf
  # containing paths in the toolchain

  list(GET QT_QTCORE_LIBRARIES 0 _lib)
  if("${_lib}" STREQUAL "debug"
      OR "${_lib}" STREQUAL "optimized"
      OR "${_lib}" STREQUAL "general")
    list(GET QT_QTCORE_LIBRARIES 1 _lib)
  endif()

  get_filename_component(_lib_path ${_lib} PATH)
  set(_plugins_path ${_lib_path}/qt4/plugins)
  file(WRITE "${QI_SDK_DIR}/${QI_SDK_BIN}/qt.conf"
"[Paths]
Plugins = ${_plugins_path}
")

  # Then, generate and install a qt.conf
  # containing relative paths
  file(WRITE "${CMAKE_BINARY_DIR}/qt.conf"
"[Paths]
Plugins = ../lib/qt4/plugins
")
  install(FILES "${CMAKE_BINARY_DIR}/qt.conf" DESTINATION bin COMPONENT runtime)

endfunction()
