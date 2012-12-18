## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


function(boost_flib _libname)
  string(TOUPPER ${_libname} _prefix)
  set(_prefix "BOOST_${_prefix}")
  clean(${_prefix})
  # Required so that FindBoost.cmake does not try to include this file
  set(Boost_NO_BOOST_CMAKE TRUE)
  if(MSVC)
    # boost program option dll does not link:
    #    main.obj : error LNK2001: unresolved external symbol
    # "public: static unsigned int const
    #    boost::program_options::options_description::m_default_line_length"
    # main.obj : error LNK2001: unresolved external symbol
    # "class std::basic_string<char,struct std::char_traits<char>,
    #                          class std::allocator<char> >
    #        boost::program_options::arg"
    # http://lists.boost.org/boost-users/2011/07/69515.php
    set(Boost_USE_STATIC_LIBS ON)
    qi_set_global(${_prefix}_DEFINITIONS  "BOOST_ALL_NO_LIB")
  endif()
  find_package(Boost COMPONENTS "${_libname}" QUIET)

  qi_set_global(${_prefix}_INCLUDE_DIRS ${Boost_INCLUDE_DIRS})
  qi_set_global(${_prefix}_LIBRARIES    ${Boost_LIBRARIES})
  export_lib(${_prefix})
endfunction()
