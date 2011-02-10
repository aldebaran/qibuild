## Copyright (C) 2011 Aldebaran Robotics

include("${T001CHAIN_DIR}/cmake/libfind.cmake")

clean(EIGEN)
fpath(EIGEN "Eigen/Eigen" Eigen PATH_SUFFIXES "eigen2")
export_header(EIGEN)

