## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# libusb-1.0 module
clean(USB_1)
fpath(USB_1 libusb-1.0/libusb.h)
fpath(USB_1 libusb.h PATH_SUFFIXES libusb-1.0)
flib(USB_1 usb-1.0)
export_lib(USB_1)
