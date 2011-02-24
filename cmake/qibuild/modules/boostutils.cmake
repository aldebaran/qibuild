## Copyright (C) 2011 Aldebaran Robotics

function(boost_flib _suffix _libname)
  set (BOOST_VERSION 1_44)
  flib(BOOST_${_suffix} OPTIMIZED NAMES
    # windows dynamic
    "boost_${_libname}-vc80-mt-${BOOST_VERSION}"
    "boost_${_libname}-vc90-mt-${BOOST_VERSION}"
    "boost_${_libname}-vc100-mt-${BOOST_VERSION}"
    # windows static
    "libboost_${_libname}-vc80-mt-${BOOST_VERSION}"
    "libboost_${_libname}-vc90-mt-${BOOST_VERSION}"
    "libboost_${_libname}-vc100-mt-${BOOST_VERSION}"

    "boost_${_libname}-xgcc40-mt-${BOOST_VERSION}"
    "boost_${_libname}-mt"
  )
  flib(BOOST_${_suffix} DEBUG NAMES
    # windows dynamic
    "boost_${_libname}-vc80-mt-gd-${BOOST_VERSION}"
    "boost_${_libname}-vc90-mt-gd-${BOOST_VERSION}"
    "boost_${_libname}-vc100-mt-gd-${BOOST_VERSION}"
    # windows static
    "libboost_${_libname}-vc80-mt-gd-${BOOST_VERSION}"
    "libboost_${_libname}-vc90-mt-gd-${BOOST_VERSION}"
    "libboost_${_libname}-vc100-mt-gd-${BOOST_VERSION}"

    "boost_${_libname}-xgcc40-mt-${BOOST_VERSION}"
    "boost_${_libname}-mt"
  )
endfunction()

function(boost_flib_static _suffix _libname)
  set (BOOST_VERSION 1_44)
  flib(BOOST_${_suffix} OPTIMIZED PATH_SUFFIXES static NAMES
                          "boost_${_libname}-mt"
                          "boost_${_libname}-xgcc40-mt-${BOOST_VERSION}"
                          "libboost_${_libname}-vc80-mt-${BOOST_VERSION}"
                          "libboost_${_libname}-vc90-mt-${BOOST_VERSION}"
                          )
  flib(BOOST_${_suffix} DEBUG PATH_SUFFIXES static NAMES
                          "boost_${_libname}-mt-d"
                          "boost_${_libname}-xgcc40-mt-1_38-${BOOST_VERSION}"
                          "libboost_${_libname}-vc80-mt-gd-1_38-${BOOST_VERSION}"
                          "libboost_${_libname}-vc90-mt-gd-1_38-${BOOST_VERSION}"
                          "boost_${_libname}-mt"
                          )
endfunction()
