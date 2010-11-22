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


clean(AVAHICOMPATDNSSD)
fpath(AVAHICOMPATDNSSD dns_sd.h PATH_SUFFIXES suffixes avahi-compat-libdns_sd)
flib(AVAHICOMPATDNSSD dns_sd)
export_lib(AVAHICOMPATDNSSD)
