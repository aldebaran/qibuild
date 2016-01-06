## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

# We tried:
#clean(UDEV)
#find_package(PkgConfig)
#pkg_check_modules(UDEV libudev)
#export_lib_pkgconfig(UDEV)
# But that did not work because UDEV_FOUND is set to 1 but UDEV_PACKAGE_FOUND is set to False
# So we use the following

clean(UDEV)
fpath(UDEV libudev.h)
flib(UDEV udev)
export_lib(UDEV)
