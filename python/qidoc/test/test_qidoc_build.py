## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
def test_simple_build(qidoc_action):
    qidoc_action.add_test_project("libqi")
    qidoc_action("build", "qi-api")
