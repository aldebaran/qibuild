## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(RUBY)
fpath(RUBY ruby/ruby.h)

flib(RUBY NAMES msvcrt-ruby18-static ruby-static)
ELSE( WIN32 )
  flib(RUBY ruby-static)
ENDIF( WIN32 )

export_lib(RUBY)
