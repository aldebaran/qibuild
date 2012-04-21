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
    <remote name="ssh-url" fetch="ssh://git@foo" />
    <remote name="http" fetch="http://foo" />
    <remote name="local" fetch="/path/to/foo" />

    <project name="ssh-bar.git" remote="ssh" />
    <project name="ssh-url-bar.git" remote="ssh-url" />
    <project name="http-bar.git" remote="http" />
    <project name="local-bar.git" remote="local" />

</manifest>
"""
        xml_in = StringIO(xml)
        manifest = qisrc.manifest.Manifest(xml_in)
        ssh_bar = manifest.get_project("ssh-bar.git")
        self.assertEquals(ssh_bar.fetch_url, "git@foo:ssh-bar.git")

        ssh_url_bar = manifest.get_project("ssh-url-bar.git")
        self.assertEquals(ssh_url_bar.fetch_url, "ssh://git@foo/ssh-url-bar.git")

        http_bar = manifest.get_project("http-bar.git")
        self.assertEquals(http_bar.fetch_url, "http://foo/http-bar.git")

        local_bar = manifest.get_project("local-bar.git")
        self.assertEquals(local_bar.fetch_url, "/path/to/foo/local-bar.git")


    def test_review_parse(self):
        xml = """
<manifest>
    <remote fetch="git@foo" review="http://gerrit"  />
    <project name="foo" review="true" />
    <project name="bar" />
</manifest>
"""
        xml_in = StringIO(xml)
        manifest = qisrc.manifest.Manifest(xml_in)
        foo = manifest.get_project("foo")
        self.assertEqual(foo.review, True)
        self.assertEqual(foo.review_url, "http://gerrit/foo")

    def test_no_remote_fetch(self):
        xml = """
<manifest>
    <remote url="git@foo" />
    <project name="bar" />
</manifest>
"""
        xml_in = StringIO(xml)
        error = None
        try:
            manifest = qisrc.manifest.Manifest(xml_in)
        except Exception, e:
            error = e
        self.assertFalse(error is None)
        self.assertTrue("remote must have a 'fetch' attribute" in str(error), error)

    def test_no_project_name(self):
        xml = """
<manifest>
    <remote fetch="git@foo" />
    <project />
</manifest>
"""
        xml_in = StringIO(xml)
        error = None
        try:
            manifest = qisrc.manifest.Manifest(xml_in)
        except Exception, e:
            error = e
        self.assertFalse(error is None)
        self.assertTrue("project must have a 'name' attribute" in str(error), error)

    def test_no_project_path(self):
        xml = """
<manifest>
    <remote fetch="git@goo" />
    <project name="bar/foo.git" />
</manifest>
"""
        xml_in = StringIO(xml)
        manifest = qisrc.manifest.Manifest(xml_in)
        project = manifest.get_project("bar/foo.git")
        self.assertEqual(project.path, "bar/foo")



if __name__ == "__main__":
    unittest.main()
