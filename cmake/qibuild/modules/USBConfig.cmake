## Copyright (C) 2011 Aldebaran Robotics

include("${T001CHAIN_DIR}/cmake/libfind.cmake")

clean(USB)
fpath(USB usb.h)
flib(USB usb)
export_lib(USB)
