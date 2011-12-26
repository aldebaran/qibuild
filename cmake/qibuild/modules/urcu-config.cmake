## Copyright (C) 2011 Aldebaran Robotics

clean(URCU)
fpath(URCU "urcu.h")
fpath(URCU "urcu/compiler.h")
flib(URCU urcu)
flib(URCU urcu-bp)
flib(URCU urcu-cds)
flib(URCU urcu-common)
flib(URCU urcu-mb)
flib(URCU urcu-qsbr)
flib(URCU urcu-signal)

export_header(URCU)
export_lib(URCU)
