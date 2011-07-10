## Copyright (C) 2011 Aldebaran Robotics

clean(ZEROMQ)
fpath(ZEROMQ zmq.h)

if(WIN32)
  flib(ZEROMQ OPTIMIZED NAMES zmq)
  flib(ZEROMQ DEBUG     NAMES zmq_d)
else()
  flib(ZEROMQ NAMES zmq)
endif()

if(UNIX)
  qi_set_global(ZEROMQ_DEPENDS "UUID")
else()
  qi_set_global(ZEROMQ_DEPENDS "WSA" "RPCRT")
endif()

export_lib(ZEROMQ)
