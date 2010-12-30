##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

#target is windows based
set(CMAKE_SYSTEM_NAME    Windows)

#needed for autotools external projects
set(QI_AUTOTOOLS_HOST     i486-mingw32)

# specify the cross compiler
set(CMAKE_C_COMPILER      i486-mingw32-gcc)
set(CMAKE_CXX_COMPILER    i486-mingw32-g++)
set(CMAKE_RC_COMPILER     i486-mingw32-windres)
set(CMAKE_AR_COMPILER     i486-mingw32-ar)
set(CMAKE_RANLIB_COMPILER i486-mingw32-ranlib)

# where is the target environment
set(CMAKE_FIND_ROOT_PATH  /usr/i486-mingw32)

# search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# for libraries and headers in the target directories
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
