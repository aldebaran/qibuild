## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# Hack here: we cannot integrate qmake in the
# qt packages in the toolchains, because qmake will report
# a path that probably does not exists, so we instead
# look for moc and uic, and the copy-paste the macros from
# QT_USE_FILE ...

# Note: when cross-compiling, you should set QT_USE_QMAKE
# to false so that we do not use qmake from the system.

if(DEFINED _QIBUILD_QT_TOOLS)
  return()
endif()

if(NOT DEFINED QT_USE_QMAKE)
  find_program(QT_QMAKE qmake)
  if(QT_QMAKE)
    set(QT_USE_QMAKE TRUE CACHE INTERNAL "" FORCE)
  else()
    set(QT_USE_QMAKE FALSE CACHE INTERNAL "" FORCE)
  endif()
endif()

if(QT_USE_QMAKE)
  # Use upstream cmake files:
  find_package(Qt4 COMPONENTS "")
  include("${QT_USE_FILE}")
  return()
endif()

find_program(QT_MOC_EXECUTABLE moc REQUIRED)
find_program(QT_UIC_EXECUTABLE uic REQUIRED)
find_program(QT_RCC_EXECUTABLE rcc REQUIRED)

if(QT_MOC_EXECUTABLE)
  qi_debug("QT_MOC_EXECUTABLE: ${QT_MOC_EXECUTABLE}")
else()
  message(FATAL_ERROR "QT_MOC not found!")
endif()

include(Qt4Macros)

qi_set_global(_QIBUILD_QT_TOOLS TRUE)
