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


clean(ACAPELATTS)
fpath(ACAPELATTS nscube.h)
#fpath(ACAPELATTS nscubeoem.h)
flib(ACAPELATTS nscube)
flib(ACAPELATTS babile)
#flib(ACAPELATTS PowerTTS-Emb_CHN)
flib(ACAPELATTS PowerTTS)
export_lib(ACAPELATTS)
