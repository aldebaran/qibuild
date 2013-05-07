""" Stores configuration for git projects in a worktree
Delegates most of the work to :py:mod:`qisrc.git`` and
:py:mod:`qisrc.review`

"""

import os
import functools

from qisys import ui
import qisys.qixml
import qisrc.git
import qisrc.review


class Remote(object):
    def __init__(self):
        self.name = None
        self.url = None
        self.review = False

    def __repr__(self):
        res = "<Remote %s: %s" % (self.name, self.url)
        if self.review:
            res += " (review)"
        res += ">"
        return res

class Branch(object):
    def __init__(self):
        self.name = None
        self.tracks = None
        self.remote_branch = None
        self.default = False

    def __repr__(self):
        return "<Branch %s (tracks: %s)>" % (self.name, self.tracks)


##
# parsing

class RemoteParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(RemoteParser, self).__init__(target)
        self._required = ["name"]

class BranchParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(BranchParser, self).__init__(target)
        self._required = ["name"]

class GitProjectParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GitProjectParser, self).__init__(target)
        self._ignore = ["worktree", "path", "clone_url", "default_branch"]
        self._required = ["src"]

    def _parse_remote(self, elem):
        remote = Remote()
        parser = RemoteParser(remote)
        parser.parse(elem)
        self.target.remotes.append(remote)

    def _parse_branch(self, elem):
        branch = Branch()
        parser = BranchParser(branch)
        parser.parse(elem)
        self.target.branches.append(branch)

    def _write_branches(self, elem):
        for branch in self.target.branches:
            parser = BranchParser(branch)
            branch_xml = parser.xml_elem()
            elem.append(branch_xml)

    def _write_remotes(self, elem):
        for remote in self.target.remotes:
            parser = RemoteParser(remote)
            remote_xml = parser.xml_elem()
            elem.append(remote_xml)
