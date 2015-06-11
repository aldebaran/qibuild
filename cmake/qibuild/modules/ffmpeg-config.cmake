## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(FFMPEG)
fpath(FFMPEG avcodec.h PATH_SUFFIXES libavcodec)
fpath(FFMPEG avdevice.h PATH_SUFFIXES libavdevice)
fpath(FFMPEG avfilter.h PATH_SUFFIXES libavfilter)
fpath(FFMPEG avformat.h PATH_SUFFIXES libavformat)
fpath(FFMPEG avresample.h PATH_SUFFIXES libavresample)
fpath(FFMPEG avutil.h PATH_SUFFIXES libavutil)
fpath(FFMPEG swresample.h PATH_SUFFIXES libswresample)
fpath(FFMPEG swscale.h PATH_SUFFIXES libswscale)

flib(FFMPEG NAMES avcodec)
flib(FFMPEG NAMES avfilter)
flib(FFMPEG NAMES avformat)
flib(FFMPEG NAMES avutil)
flib(FFMPEG NAMES avresample)
flib(FFMPEG NAMES swscale)
flib(FFMPEG NAMES swresample)

qi_persistent_set(FFMPEG_DEPENDS ZLIB PTHREAD BZIP2)

export_lib(FFMPEG)

