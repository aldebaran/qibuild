## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest
from qibuild.test.test_toc import TestToc

# pylint: disable-msg=E1101
@pytest.mark.slow
def test_build():
    with TestToc() as toc:
        proj = toc.get_project("submodule")
        toc.configure_project(proj)
        toc.build_project(proj)
