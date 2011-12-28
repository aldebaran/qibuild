## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Automatic testing for qibuild.project.ProjectConfig

"""

import os
import qibuild
import unittest
from StringIO import StringIO

def cfg_from_string(str, user_config=None):
    cfg_loc = StringIO(str)
    project_cfg = qibuild.config.ProjectConfig()
    project_cfg.read(cfg_loc)
    return project_cfg

class ProjectConfigTestClass(unittest.TestCase):

    def test_simple_read(self):
        xml = """
<project name="foo" />
"""
        project_cfg = cfg_from_string(xml)
        self.assertEqual(project_cfg.name, "foo")

    def test_read_depends(self):
        xml = """
<project name="foo">
    <depends name="bar" />
    <depends name="baz" />
    <rdepends name="spam" />
</project>
"""
        project_cfg = cfg_from_string(xml)
        self.assertEqual(project_cfg.depends, ["bar", "baz"])
        self.assertEqual(project_cfg.rdepends, ["spam"])


if __name__ == "__main__":
    unittest.main()



