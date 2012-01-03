## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OGRE)
fpath(OGRE OgreRoot.h PATH_SUFFIXES ogre OGRE)
flib(OGRE OPTIMIZED NAMES OgreMain Ogre)
flib(OGRE DEBUG     NAMES OgreMain_d OgreMain Ogre)
if (UNIX AND NOT APPLE)
  flib(OGRE freeimage)
endif()
export_lib(OGRE)
