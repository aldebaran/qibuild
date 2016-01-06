## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(qi_set_qt_plugin_properties target)
  if(CMAKE_MAJOR_VERSION LESS 3)
    get_target_property(RELEASE_DEF "${target}" COMPILE_DEFINITIONS_RELEASE)
    get_target_property(DEBUG_DEF "${target}" COMPILE_DEFINITIONS_DEBUG)
    set_target_properties("${target}"
      PROPERTIES
      COMPILE_DEFINITIONS_RELEASE "${RELEASE_DEF};QT_SHARED;QT_PLUGIN;QT_NO_DEBUG"
      COMPILE_DEFINITIONS_DEBUG "${DEBUG_DEF};QT_SHARED;QT_PLUGIN;QT_DEBUG"
    )
  else()
    get_target_property(DEF "${target}" COMPILE_DEFINITIONS)
    set_target_properties("${target}"
      PROPERTIES
      COMPILE_DEFINITIONS "${DEF};QT_SHARED;QT_PLUGIN;$<$<CONFIG:Release>:QT_NO_DEBUG>$<$<CONFIG:Debug>:QT_DEBUG>"
    )
  endif()
endfunction()
