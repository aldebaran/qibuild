## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(OGRE)
fpath(OGRE OgreRoot.h PATH_SUFFIXES ogre OGRE)
find_path(OGRE_PREQ_PATH OgrePrerequisites.h PATH_SUFFIXES ogre OGRE)

flib(OGRE OPTIMIZED NAMES OgreMain Ogre)
flib(OGRE DEBUG     NAMES OgreMain_d OgreMain Ogre)

function(get_preprocessor_entry VARIABLE)
  string(REGEX MATCH "# *define +${VARIABLE} +((\"([^\n]*)\")|([^ \n]*))" _there "${ARGN}")
  if (CMAKE_MATCH_3)
    set(${VARIABLE} "${CMAKE_MATCH_3}" PARENT_SCOPE)
  else(CMAKE_MATCH_4)
    set(${VARIABLE} "${CMAKE_MATCH_4}" PARENT_SCOPE)
  else()
    set(${VARIABLE} "0" PARENT_SCOPE)
  endif ()
endfunction()

# determine Ogre version
file(READ ${OGRE_PREQ_PATH}/OgrePrerequisites.h OGRE_TEMP_VERSION_CONTENT)
get_preprocessor_entry(OGRE_VERSION_MAJOR ${OGRE_TEMP_VERSION_CONTENT})
get_preprocessor_entry(OGRE_VERSION_MINOR ${OGRE_TEMP_VERSION_CONTENT})
get_preprocessor_entry(OGRE_VERSION_PATCH ${OGRE_TEMP_VERSION_CONTENT})
set(OGRE_VERSION "${OGRE_VERSION_MAJOR}.${OGRE_VERSION_MINOR}.${OGRE_VERSION_PATCH}")

message(STATUS "Found Ogre (${OGRE_VERSION})")

if (${OGRE_VERSION} VERSION_GREATER "1.8.99")
  flib(OGRE OPTIMIZED NAMES OgreOverlay)
  flib(OGRE DEBUG     NAMES OgreOverlay_d OgreOverlay)
endif()

if (UNIX AND NOT APPLE)
  flib(OGRE freeimage)
endif()
export_lib(OGRE)
