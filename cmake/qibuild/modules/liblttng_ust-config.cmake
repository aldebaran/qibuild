## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(LIBLTTNG_UST)
fpath(LIBLTTNG_UST "lttng/tracepoint.h")
flib(LIBLTTNG_UST "lttng-ust")

export_header(LIBLTTNG_UST)
export_lib(LIBLTTNG_UST)

