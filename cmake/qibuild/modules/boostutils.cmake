## Copyright (C) 2011 Aldebaran Robotics

function(boost_flib _suffix _libname)
  flib(BOOST_${_suffix} OPTIMIZED NAMES
                          "boost_${_libname}-mt"
                          "boost_${_libname}-xgcc40-mt-1_44"
                          "libboost_${_libname}-vc80-mt-1_44"
                          "libboost_${_libname}-vc90-mt-1_44"
                          )
  flib(BOOST_${_suffix} DEBUG NAMES
                          "boost_${_libname}-mt-d"
                          "boost_${_libname}-xgcc40-mt-1_44"
                          "libboost_${_libname}-vc80-mt-gd-1_44"
                          "libboost_${_libname}-vc90-mt-gd-1_44"
                          "boost_${_libname}-mt"
                          )
endfunction()

function(boost_flib_static _suffix _libname)
  flib(BOOST_${_suffix} OPTIMIZED PATH_SUFFIXES static NAMES
                          "boost_${_libname}-mt"
                          "boost_${_libname}-xgcc40-mt-1_44"
                          "libboost_${_libname}-vc80-mt-1_44"
                          "libboost_${_libname}-vc90-mt-1_44"
                          )
  flib(BOOST_${_suffix} DEBUG PATH_SUFFIXES static NAMES
                          "boost_${_libname}-mt-d"
                          "boost_${_libname}-xgcc40-mt-1_44"
                          "libboost_${_libname}-vc80-mt-gd-1_44"
                          "libboost_${_libname}-vc90-mt-gd-1_44"
                          "boost_${_libname}-mt"
                          )
endfunction()
