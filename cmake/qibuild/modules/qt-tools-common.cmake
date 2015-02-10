## Copyright (c) 2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(qi_set_qt_plugin_properties target)
  if(CMAKE_MAJOR_VERSION LESS 3)
    set_target_properties("${target}"
      PROPERTIES
      COMPILE_DEFINITIONS_RELEASE "QT_SHARED;QT_PLUGIN;QT_NO_DEBUG"
      COMPILE_DEFINITIONS_DEBUG "QT_SHARED;QT_PLUGIN;QT_DEBUG"
    )
  else()
    set_target_properties("${target}"
      PROPERTIES
      COMPILE_DEFINITIONS "QT_SHARED;QT_PLUGIN;$<$<CONFIG:Release>:QT_NO_DEBUG>$<$<CONFIG:Debug>:QT_DEBUG>"
    )
  endif()
endfunction()
