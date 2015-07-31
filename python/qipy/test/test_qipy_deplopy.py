## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qibuild.test.test_qibuild_deploy import get_ssh_url

def test_simple(qipy_action, tmpdir):
    url = get_ssh_url(tmpdir)
    qipy_action.add_test_project("a_lib")
    qipy_action("deploy", "a", "--url", url)
    assert tmpdir.join("lib", "python2.7", "site-packages", "a.py").check(file=True)
