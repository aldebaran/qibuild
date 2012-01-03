## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(ZEROMQ)
fpath(ZEROMQ zmq.h PATH_SUFFIXES zmq)

if(WIN32)
  # For some reason, it's zmq on vs2010 and libzmq on vs2008
  flib(ZEROMQ OPTIMIZED NAMES libzmq   zmq)
  flib(ZEROMQ DEBUG     NAMES libzmq_d zmq_d)
else()
  flib(ZEROMQ NAMES zmq)
endif()

if(UNIX)
  qi_set_global(ZEROMQ_DEPENDS "UUID")
else()
  qi_set_global(ZEROMQ_DEPENDS "WSA" "RPCRT")
endif()

export_lib(ZEROMQ)
