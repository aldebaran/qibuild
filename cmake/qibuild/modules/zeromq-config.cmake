## Copyright (C) 2011 Aldebaran Robotics

clean(ZEROMQ)
fpath(ZEROMQ zmq.h)
flib(ZEROMQ OPTIMIZED NAMES libzmq zmq)
flib(ZEROMQ DEBUG     NAMES libzmq zmq_d)
if(UNIX)
  qi_set_global(ZEROMQ_DEPENDS "UUID")
else()
  qi_set_global(ZEROMQ_DEPENDS "WSA" "RPCRT")
endif()
export_lib(ZEROMQ)
