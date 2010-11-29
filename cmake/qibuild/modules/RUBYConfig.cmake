##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008 Aldebaran Robotics



clean(RUBY)
fpath(RUBY ruby/ruby.h)

IF( WIN32 )
  flib(RUBY msvcrt-ruby18-static)
ELSE( WIN32 )
  flib(RUBY ruby-static)
ENDIF( WIN32 )

export_lib(RUBY)
