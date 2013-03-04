## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qibuild with coverage option

"""

import os
import pytest

import qibuild
import qibuild.test
import qibuild.gcov
from qibuild.test.test_toc import TestToc


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_with_coverage():
    with TestToc() as toc:
        proj = toc.get_project("cov")
        toc.configure_project(proj, coverage=True)
        toc.build_project(proj)
        qibuild.gcov.generate_coverage_xml_report(proj)
        for name in [proj.name + ".xml"]:
            expected_path = os.path.join(proj.build_directory, name)
            assert os.path.exists(expected_path)

