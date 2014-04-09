## Copyright (C) 2011-2014 Aldebaran Robotics

clean(LIBURCU)
fpath(LIBURCU "urcu.h")
fpath(LIBURCU "urcu/compiler.h")
flib(LIBURCU urcu)
flib(LIBURCU urcu-bp)
flib(LIBURCU urcu-cds)
flib(LIBURCU urcu-common)
flib(LIBURCU urcu-mb)
flib(LIBURCU urcu-qsbr)
flib(LIBURCU urcu-signal)

export_header(LIBURCU)
export_lib(LIBURCU)
