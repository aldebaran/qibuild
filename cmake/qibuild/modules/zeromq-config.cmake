## Copyright (C) 2011 Aldebaran Robotics

clean(ZEROMQ)
fpath(ZEROMQ zmq.h)

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
