## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(HDF5_CPP)
fpath(HDF5_CPP H5Cpp.h)
flib(HDF5_CPP hdf5_cpp)
qi_persistent_set(HDF5_CPP_DEPENDS "HDF5")
export_lib(HDF5_CPP)
