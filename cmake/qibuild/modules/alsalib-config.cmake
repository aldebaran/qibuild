## Copyright (C) 2011 Aldebaran Robotics



clean(ALSALIB)

if (NOT TARGET_HOST STREQUAL "TARGET_HOST_WINDOWS")
  fpath(ALSALIB alsa/asoundlib.h)
  flib(ALSALIB asound)
endif()

export_lib(ALSALIB)
