## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(BFL)
fpath(BFL bfl/bfl_constants.h)

flib(BFL NAMES orocos-bfl)
export_lib(BFL)
