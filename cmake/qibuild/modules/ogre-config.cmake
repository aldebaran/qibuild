##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2011 Aldebaran Robotics

clean(OGRE)
fpath(OGRE OgreRoot.h PATH_SUFFIXES ogre OGRE)
flib(OGRE OPTIMIZED NAMES OgreMain Ogre )
flib(OGRE DEBUG     NAMES OgreMain_d OgreMain Ogre)
if (UNIX AND NOT APPLE)
  flib(OGRE freeimage)
endif()
export_lib(OGRE)
