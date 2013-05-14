""" Stores configuration for git projects in a worktree
Delegates most of the work to :py:mod:`qisrc.git`` and
:py:mod:`qisrc.review`

"""

import re
import os

import qisys.qixml
import qisrc.git
import qisrc.review


class Remote(object):
    def __init__(self):
        self.name = None
        self.url = None
        self.review = False

        # used when joining the remote with a project name
        self.prefix = None

        # used for gerrit setup
        self.protocol = None
        self.username = None
        self.server = None
        self.port = None

    def parse_url(self):
        full_ssh = re.compile("""
                        ssh://
                        ((?P<username>[^@]+)@)?
                        (?P<server>[^:/]+)
                        (:(?P<port>\d+))?
                        (?P<subfolder>.*)
                        """, re.VERBOSE)
        ssh_url = re.compile("""
                        (?P<username>.*?)
                        @
                        (?P<server>.*)
                        (?P<sep>[:/])?
                        (?P<subfolder>)
                        """, re.VERBOSE)
        other_url = re.compile("""
                        ((?P<protocol>(git|http|https|file))://)
                        (?P<server>[^:/]+)
                        (:(?P<port>\d+))?
                        """, re.VERBOSE)
        match = re.match(full_ssh, self.url)
        if match:
            self.protocol = "ssh"
            groupdict = match.groupdict()
            self.server = groupdict["server"]
            port = groupdict.get("port")
            if port:
                self.port = int(port)
            username = groupdict.get("username")
            if username:
                self.username = username
            else:
                username = qisrc.review.get_gerrit_username(self.server,
                                                            ssh_port=self.port)
                if not username:
                    raise Exception("Could not guess ssh username")
                self.username = username
            prefix =  "ssh://%s@%s" % (username, self.server)
            if self.port:
                prefix += ":%i" % self.port
            subfolder = groupdict.get("subfolder", "")
            prefix += subfolder
            if not prefix.endswith("/"):
                prefix += "/"
            self.prefix = prefix
            return

        match = re.match(ssh_url, self.url)
        if match:
            groupdict = match.groupdict()
            self.protocol = "ssh"
            self.username = groupdict["username"]
            self.server = groupdict["server"]
            sep = groupdict["sep"] or ":"
            subfolder = groupdict.get("subfolder", "")
            self.prefix = "%s@%s%s%s" % (self.username, self.server, sep,
                                         subfolder)
            return

        match = re.match(other_url, self.url)
        if match:
            groupdict = match.groupdict()
            self.protocol = groupdict["protocol"]
            self.server = groupdict["server"]
            port = groupdict.get("port")
            if port:
                self.port = int(port)
            self.prefix = self.url
            if not self.prefix.endswith("/"):
                self.prefix += "/"
            return

        if os.path.exists(self.url):
            prefix = qisys.sh.to_native_path(self.url)
            prefix += os.path.sep
            self.prefix = prefix

        if not self.prefix:
            raise Exception("Could not parse %s as a git url" % self.url)


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

