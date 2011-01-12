##
## boosttools.cmake
## Login : <ctaf@cgestes-de>
## Started on  Mon Oct 19 14:29:49 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##

function(boost_flib _suffix _libname)
  flib(BOOST_${_suffix} OPTIMIZED NAMES
                          "boost_${_libname}-mt"
                          "boost_${_libname}-xgcc40-mt-1_38"
                          "libboost_${_libname}-vc80-mt-1_38"
                          "libboost_${_libname}-vc90-mt-1_38"
                          )
  flib(BOOST_${_suffix} DEBUG NAMES
                          "boost_${_libname}-mt-d"
                          "boost_${_libname}-xgcc40-mt-1_38"
                          "libboost_${_libname}-vc80-mt-gd-1_38"
                          "libboost_${_libname}-vc90-mt-gd-1_38"
                          "boost_${_libname}-mt"
                          )
endfunction(boost_flib _suffix _libname)

function(boost_flib_static _suffix _libname)
  flib(BOOST_${_suffix} OPTIMIZED PATH_SUFFIXES static NAMES
                          "boost_${_libname}-mt"
                          "boost_${_libname}-xgcc40-mt-1_38"
                          "libboost_${_libname}-vc80-mt-1_38"
                          "libboost_${_libname}-vc90-mt-1_38"
                          )
  flib(BOOST_${_suffix} DEBUG PATH_SUFFIXES static NAMES
                          "boost_${_libname}-mt-d"
                          "boost_${_libname}-xgcc40-mt-1_38"
                          "libboost_${_libname}-vc80-mt-gd-1_38"
                          "libboost_${_libname}-vc90-mt-gd-1_38"
                          "boost_${_libname}-mt"
                          )
endfunction(boost_flib_static _suffix _libname)
