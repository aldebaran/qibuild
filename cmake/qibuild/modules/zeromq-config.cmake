## Copyright (C) 2011 Aldebaran Robotics

clean(ZEROMQ)
fpath(ZEROMQ zmq.h)
flib(ZEROMQ zmq)
if(UNIX)
  set(ZEROMQ_DEPENDS "UUID")
else()
  set(ZEROMQ_DEPENDS WSA RPCRT)
endif()
export_lib(ZEROMQ)
