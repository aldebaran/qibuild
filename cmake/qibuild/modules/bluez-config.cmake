## Copyright (C) 2011 Aldebaran Robotics



clean(BLUEZ)

if (NOT TARGET_HOST STREQUAL "TARGET_HOST_WINDOWS")
  fpath(BLUEZ bluetooth/bluetooth.h)
  flib(BLUEZ bluetooth)
endif()

export_lib(BLUEZ)
