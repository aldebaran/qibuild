## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
clean(REDLAND)

fpath(REDLAND redland.h)
flib(REDLAND NAMES rdf)
export_lib(REDLAND)
