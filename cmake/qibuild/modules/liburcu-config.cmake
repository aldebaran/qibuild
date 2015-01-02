## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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
