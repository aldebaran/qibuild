## Copyright (C) 2011 Aldebaran Robotics

clean(RUBY)
fpath(RUBY ruby/ruby.h)

flib(RUBY NAMES msvcrt-ruby18-static ruby-static)
ELSE( WIN32 )
  flib(RUBY ruby-static)
ENDIF( WIN32 )

export_lib(RUBY)
