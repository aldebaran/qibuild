## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(FFMPEG)
fpath(FFMPEG libavcodec/avcodec.h)

flib(FFMPEG NAMES avcodec)
flib(FFMPEG NAMES avfilter)
flib(FFMPEG NAMES avformat)
flib(FFMPEG NAMES avutil)
flib(FFMPEG NAMES avresample)
flib(FFMPEG NAMES swscale)
flib(FFMPEG NAMES swresample)

qi_persistent_set(FFMPEG_DEPENDS ZLIB PTHREAD BZIP2)

export_lib(FFMPEG)

