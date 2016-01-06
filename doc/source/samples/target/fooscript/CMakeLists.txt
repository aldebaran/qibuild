## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

project(FooScript NONE)



qi_create_script(MYSCRIPT myscript.py myscript.py)
qi_stage_script(myscript.py)
