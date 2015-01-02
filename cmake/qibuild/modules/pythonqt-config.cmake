## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

clean(PYTHONQT)

fpath(PYTHONQT PythonQt.h PATH_SUFFIXES PythonQt)
flib(PYTHONQT PythonQt)

export_lib(PYTHONQT)
