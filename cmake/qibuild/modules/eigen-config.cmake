## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(EIGEN)
fpath(EIGEN "Eigen/Eigen" Eigen PATH_SUFFIXES "eigen2")
export_header(EIGEN)

