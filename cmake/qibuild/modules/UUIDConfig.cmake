##
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Oct  6 18:19:18 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Jean-Charles DELAY <jdelay@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics



if(APPLE)
  set(UUID_IN_SYSTEM "SYSTEM")
else()
  set(UUID_IN_SYSTEM "")
endif()

clean(UUID)

fpath(UUID uuid/uuid.h ${UUID_IN_SYSTEM})
if (NOT APPLE)
  flib (UUID uuid   ${UUID_IN_SYSTEM})
  export_lib(UUID)
else()
  export_header(UUID)
endif()
