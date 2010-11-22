##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(ACAPELAASR)
fpath(ACAPELAASR EarSDK.h)
fpath(ACAPELAASR PowerASRChn.h)
fpath(ACAPELAASR PowerASREmb.h)
#flib(ACAPELAASR PowerASR)
flib(ACAPELAASR PowerASRChn)
flib(ACAPELAASR babear)
flib(ACAPELAASR fsg2car)
flib(ACAPELAASR EarBundle)
export_lib(ACAPELAASR)
