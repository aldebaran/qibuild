## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(BOOST_TR1)
fpath(BOOST_TR1 memory PATH_SUFFIXES boost/tr1/tr1)
fpath(BOOST_TR1 boost/config.hpp)
export_header(BOOST_TR1)
