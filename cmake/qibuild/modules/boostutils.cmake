## Copyright (C) 2011 Aldebaran Robotics

function(boost_flib _suffix _libname)
  set (BOOST_VERSION 1_44)
  flib(BOOST_${_suffix} OPTIMIZED NAMES
    # windows vs dynamic
    "boost_${_libname}-vc80-mt-${BOOST_VERSION}"
    "boost_${_libname}-vc90-mt-${BOOST_VERSION}"
    "boost_${_libname}-vc100-mt-${BOOST_VERSION}"
    # windows vs static
    "libboost_${_libname}-vc80-mt-${BOOST_VERSION}"
    "libboost_${_libname}-vc90-mt-${BOOST_VERSION}"
    "libboost_${_libname}-vc100-mt-${BOOST_VERSION}"
    # mingw
    "libboost_${_libname}-mgw44-mt-${BOOST_VERSION}"
    # osx
    "boost_${_libname}-xgcc40-mt-${BOOST_VERSION}"

    # linux
    "boost_${_libname}-mt"
    "boost_${_libname}"
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
    # mingw
    "libboost_${_libname}-mgw44-mt-d-${BOOST_VERSION}"

    # osx
    "boost_${_libname}-xgcc40-mt-${BOOST_VERSION}"

    # linux
    "boost_${_libname}_d"
    "boost_${_libname}-mt"
    "boost_${_libname}"
  )
endfunction()
