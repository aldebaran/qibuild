## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(LTTNG_TOOLS)
fpath(LTTNG_TOOLS "lttng/lttng.h")
flib(LTTNG_TOOLS "lttng-ctl")

export_header(LTTNG_TOOLS)
export_lib(LTTNG_TOOLS)

