## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import unittest
from StringIO import StringIO

import qisrc.manifest



class ManifestTestCase(unittest.TestCase):

    def test_parse(self):
        xml = """
<manifest>
    <remote name="origin"
        fetch="git@git.aldebaran.lan"
        review="{name}@gerrit.aldebaran.lan"
    />
</manifest>
"""
        xml_in = StringIO(xml)
        manifest = qisrc.manifest.Manifest(xml_in)
        self.assertEquals(len(manifest.projects), 0)

    def test_simple_parse(self):
        xml = """
<manifest>
    <remote name="origin"
        fetch="git@git.aldebaran.lan"
    />

    <project name="qi/libqi.git"
        path="lib/libqi"
    />
</manifest>
"""
        xml_in = StringIO(xml)
        manifest = qisrc.manifest.Manifest(xml_in)
        self.assertEquals(len(manifest.projects), 1)
        libqi = manifest.projects[0]
        self.assertEquals(libqi.fetch_url, "git@git.aldebaran.lan:qi/libqi.git")
        self.assertEquals(libqi.path, "lib/libqi")


    def test_various_url_formats(self):
        xml = """
<manifest>
    <remote name="ssh" fetch="git@foo" />
    <remote name="http" fetch="http://foo" />
    <remote name="local" fetch="/path/to/foo" />

    <project name="ssh-bar.git" remote="ssh" />
    <project name="http-bar.git" remote="http" />
    <project name="local-bar.git" remote="local" />

</manifest>
"""
        xml_in = StringIO(xml)
        manifest = qisrc.manifest.Manifest(xml_in)
        ssh_bar = manifest.get_project("ssh-bar.git")
        self.assertEquals(ssh_bar.fetch_url, "git@foo:ssh-bar.git")

        http_bar = manifest.get_project("http-bar.git")
        self.assertEquals(http_bar.fetch_url, "http://foo/http-bar.git")

        local_bar = manifest.get_project("local-bar.git")
        self.assertEquals(local_bar.fetch_url, "/path/to/foo/local-bar.git")



if __name__ == "__main__":
    unittest.main()
