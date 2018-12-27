## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
include("${_ROOT_DIR}/qt-tools-common.cmake")

# This is called *before* any call to qi_use_lib() is made.
# Here we need to define the qt macros, such as qt5_wrap_cpp,
# qt5_add_resources, qt5_wrap_ui
set(CMAKE_AUTOMOC ON)
find_package(Qt5Core REQUIRED)
include("${Qt5Core_DIR}/Qt5CoreMacros.cmake")

set(_qt5_widggets_dir ${Qt5Core_DIR}/../Qt5Widgets)
find_package(Qt5Widgets QUIET NO_DEFAULT_PATH
  PATHS "${Qt5Core_DIR}/..")
if(Qt5Widgets_FOUND)
  include("${Qt5Widgets_DIR}/Qt5WidgetsMacros.cmake")
endif()

macro(qt5_add_resources name)
  _qt5_add_resources(${name} ${ARGN})
  set_property(SOURCE ${${name}} PROPERTY SKIP_AUTOMOC ON)
endmacro()

function(qi_generate_qt_conf)
  # First, find qt and generate qt.conf
  # containing paths in the toolchain
  if(DEFINED QT_PLUGINS_PATH)
    set(_plugins_path "${QT_PLUGINS_PATH}")
  else()
    list(GET QT5_CORE_LIBRARIES 0 _lib)
    if("${_lib}" STREQUAL "debug"
        OR "${_lib}" STREQUAL "optimized"
        OR "${_lib}" STREQUAL "general")
      list(GET QT5_CORE_LIBRARIES 1 _lib)
    endif()
    if(TARGET ${_lib})
      get_target_property(_lib_loc ${_lib} LOCATION)
    else()
      set(_lib_loc ${_lib})
    endif()
    get_filename_component(_lib_path ${_lib_loc} PATH)
    if(APPLE)
      # location is: <prefix>/lib/QtCore.framework/QtCore
      get_filename_component(_lib_path ${_lib_path} PATH)
    endif()
    get_filename_component(_root_path ${_lib_path} PATH)
  endif()

  if(NOT EXISTS ${_root_path}/plugins)
    # No need to write a qt.conf if the prefix is not
    # correct.
    # When not using a toolchain, the qt.conf file is
    # not necessary anyways.
    return()
  endif()

  file(WRITE "${QI_SDK_DIR}/${QI_SDK_BIN}/qt.conf"
"[Paths]
Plugins = ${_root_path}/plugins
Qml2Imports = ${_root_path}/qml
Translations = ${_root_path}/translations
")

  # Then, generate and install a qt.conf
  # containing relative paths
  file(WRITE "${CMAKE_BINARY_DIR}/qt.conf"
"[Paths]
Plugins = ../plugins
Qml2Imports = ../qml
Translations = ../translations
")
  install(FILES "${CMAKE_BINARY_DIR}/qt.conf" DESTINATION bin COMPONENT runtime)

endfunction()
