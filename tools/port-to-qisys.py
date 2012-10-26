"""
A quick script to port existing python code to
qisys
Requires replacer:
  https://github.com/ctaf42/ctafconf/blob/master/bin/replacer
"""

import subprocess

for (old, new) in [
      ("qibuild.archive"                ,  "qisys.archive"),
      ("qibuild.command"                ,  "qisys.command"),
      ("qibuild.envsetter"              ,  "qisys.envsetter"),
      ("qibuild.external"               ,  "qisys.external"),
      ("qibuild.interact"               ,  "qisys.interact"),
      ("qibuild.script"                 ,  "qisys.script"),
      ("qibuild.sh"                     ,  "qisys.sh"),
      ("qibuild.ui"                     ,  "qisys.ui"),
      ("qisrc.worktree"                 ,  "qisys.worktree"),
      ("qitoolchain.remote"             ,  "qisys.remote"),
      ("qitoolchain.version"            ,  "qisys.version"),
      ("qibuild.run_action"             ,  "qisys.script.run_action"),
      ("qibuild.toc_open"               ,  "qibuild.toc.toc_open"),
      ("qisrc.open_worktree"            ,  "qisys.worktree.open_worktree"),
      ("from qibuild import ui"         ,  "from qisys import ui"),
      ("qibuild.parsers.default_parser" ,  "qisys.parsers.default_parser"),
      ("qibuild.parsers.worktree_parser",  "qisys.parsers.worktree_parser")
]:
    cmd = ["replacer", old, new, "--no-backup", "--go"]
    subprocess.check_call(cmd)
