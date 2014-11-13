##
# This is called *before* any call to qi_use_lib() is made.
# Here we need to define the qt macros, such as qt5_wrap_cpp,
# qt5_add_resources, qt5_wrap_ui
set(CMAKE_AUTOMOC ON)
find_package(Qt5Core REQUIRED)
include("${Qt5Core_DIR}/Qt5CoreMacros.cmake")

find_package(Qt5Widgets REQUIRED)
include("${Qt5Widgets_DIR}/Qt5WidgetsMacros.cmake")

