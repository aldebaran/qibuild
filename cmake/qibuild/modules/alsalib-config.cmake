## Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(ALSALIB)
fpath(ALSALIB alsa/asoundlib.h)
flib(ALSALIB asound)
export_lib(ALSALIB)
