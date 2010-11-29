##
## layout.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Sun Oct 18 21:45:51 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

#standard layout for an sdk

#warning findmodule.*.sdk.in and sdk.cmake use implicit relative path
#between _SDK_LIB and _SDK_CMAKE_MODULES, name could be change, but
#the relative path between each var should remain the same.
qi_set_global(QI_SDK_BIN            "bin"              )
qi_set_global(QI_SDK_LIB            "lib"              )
qi_set_global(QI_SDK_FRAMEWORK      "Frameworks"       )
qi_set_global(QI_SDK_INCLUDE        "include"          )
qi_set_global(QI_SDK_SHARE          "share"            )
qi_set_global(QI_SDK_CONF           "etc"              )
qi_set_global(QI_SDK_DOC            "share/doc"        )
qi_set_global(QI_SDK_CMAKE          "lib/cmake"        )
qi_set_global(QI_SDK_CMAKE_MODULES  "lib/cmake/modules")

#WINDOWS SDK LAYOUT
set(WIN_LAYOUT_SDK_BIN            ""                      CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_LIB            "dev/lib"               CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_INCLUDE        "dev/include"           CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_SHARE          "data"                  CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_CONF           "preferences"           CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_DOC            "doc"                   CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_CMAKE          "dev/cmake"             CACHE STRING "" FORCE)
set(WIN_LAYOUT_SDK_CMAKE_MODULES  "dev/cmake/modules"     CACHE STRING "" FORCE)


#TODO: sdk are arch dependant
# set(_SDK_BIN            "${SDK_ARCH}/bin"                   CACHE STRING "" FORCE)
# set(_SDK_LIB            "${SDK_ARCH}/lib"                   CACHE STRING "" FORCE)
# set(_SDK_INCLUDE        "${SDK_ARCH}/include"               CACHE STRING "" FORCE)
# set(_SDK_SHARE          "${SDK_ARCH}/share"                 CACHE STRING "" FORCE)
# set(_SDK_CONF           "${SDK_ARCH}/etc"                   CACHE STRING "" FORCE)
# set(_SDK_DOC            "${SDK_ARCH}/share/doc"             CACHE STRING "" FORCE)
# set(_SDK_CMAKE          "${SDK_ARCH}/lib/cmake"             CACHE STRING "" FORCE)
# set(_SDK_CMAKE_MODULES  "${SDK_ARCH}/lib/cmake/modules"     CACHE STRING "" FORCE)


mark_as_advanced(QI_SDK_BIN
                 QI_SDK_LIB
                 QI_SDK_INCLUDE
                 QI_SDK_SHARE
                 QI_SDK_CONF
                 QI_SDK_DOC
                 QI_SDK_CMAKE
                 QI_SDK_CMAKE_MODULES)
