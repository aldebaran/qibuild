## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(HDF5)
fpath(HDF5 hdf5.h)
flib(HDF5 hdf5)
qi_persistent_set(HDF5_DEPENDS "PTHREAD" "ZLIB" "M")
export_lib(HDF5)
