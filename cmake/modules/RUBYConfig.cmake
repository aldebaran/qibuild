##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/libfind.cmake")

clean(RUBY)
fpath(RUBY ruby/ruby.h PATH_SUFFIXES ruby-1.9.1)
fpath(RUBY ruby/config.h PATH_SUFFIXES ruby-1.9.1/x86_64-linux )

IF( WIN32 )
  flib(RUBY msvcrt-ruby18-static)
ELSE( WIN32 )
  flib(RUBY ruby-static ruby)
ENDIF( WIN32 )

export_lib(RUBY)
