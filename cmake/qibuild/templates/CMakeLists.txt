##
## CMakeLists.txt
## Login : <ctaf@localhost.localdomain>
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  DESTINATION "${_SDK_CMAKE}/"
  USE_SOURCE_PERMISSIONS
  COMPONENT cmake
  PATTERN "CMakeLists.txt" EXCLUDE
  )
