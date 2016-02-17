## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisys.test.conftest import skip_deploy, local_url

@skip_deploy
def test_simple(qipy_action, tmpdir, local_url):
    qipy_action.add_test_project("a_lib")
    qipy_action("deploy", "a", "--url", local_url)
    assert tmpdir.join("lib", "python2.7", "site-packages", "a.py").check(file=True)
