## Copyright (C) 2011 Aldebaran Robotics

# Note: find_library(wsock) won't work because it would
# return c:\windows\system32\wscock32.dll ...

# Also, we do not need any additional include dirs to
# use wsock32, but we need WSOCK_INCLUDE_DIR for
# export_lib() to be happy

clean(WSOCK)
set(WSOCK_INCLUDE_DIR " " CACHE STRING "" FORCE)
if(MSCV)
  set(WSOCK_LIBRARIES wsock32.lib CACHE STRING "" FORCE)
else()
  set(WSOCK_LIBRARIES wsock32 CACHE STRING "" FORCE)
endif()
export_lib(WSOCK)

