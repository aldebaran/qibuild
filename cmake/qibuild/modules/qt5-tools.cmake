##
# This is called *before* any call to qi_use_lib() is made.
# Here we need to define the qt macros, such as qt5_wrap_cpp,
# qt5_add_resources, qt5_wrap_ui
set(CMAKE_AUTOMOC ON)
find_package(Qt5Core REQUIRED)
include("${Qt5Core_DIR}/Qt5CoreMacros.cmake")

find_package(Qt5Widgets REQUIRED)
include("${Qt5Widgets_DIR}/Qt5WidgetsMacros.cmake")

# Since upstream uses imported targets (with Qt5::Widgets for instance),
# we need to call find_package() at every run so that imported targets are found.
# We cannot do it in the qibuild/modules/qt5_*-config.cmake because
# of the PACKAGE_FOUND optimization used by qi_use_lib()
find_package(Qt5Concurrent)
find_package(Qt5Ftp)
find_package(Qt5Network)
find_package(Qt5Script)
find_package(Qt5Sql)
find_package(Qt5Test)
find_package(Qt5Xml)
