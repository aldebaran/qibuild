#!/usr/bin/env python
##
## Author(s):
##  -  <>
##
## (is it fantomas?)
##
## Copyright (C) 2010 Aldebaran Robotics
##

#fold into actions, generate an asciidoc manpage
import sys
import qibuild.shell

TEMPLATE = """QIBUILD(1)
==========
:doctype: manpage


NAME
----
qibuild - get, build, install projects.


SYNOPSIS
--------
*qibuild* ['OPTIONS'] COMMAND ['COMMAND_OPTIONS'] ARGUMENTS


DESCRIPTION
-----------
The command line program toc provide severals actions to work with projects.


COMMANDS
--------
%s


OPTIONS
-------
*--toc-work-tree='TOC_WORK_TREE'::
    Specify the toc work tree. This can be an environment variable too.

*-h, --help* ['TOPIC']::
    Print help TOPIC. *--help* 'topics' will print a list of help
    topics, *--help*='syntax' summarizes AsciiDoc syntax,
    *--help*='manpage' prints the AsciiDoc manpage.

*-v, --verbose*::
    Print verbose output.


EXIT STATUS
-----------
*0*::
    Success

*1*::
    Failure


BUGS
----
    th3r3 15 n0 5p00n
"""

if __name__ == "__main__":
    outfile = sys.argv[1]
    actions = list()
    actions.extend(qibuild.shell.main.action_modules_from_package("qibuild.actions"))

    max_len = 0
    for action in actions:
        action_len = len(action.__name__[16:].strip())
        if action_len > max_len:
            max_len = action_len

    output = list()
    for action in actions:
        action_doc = "TODO: documentation"
        action_name = action.__name__[16:].strip().replace(".", " ")
        if action.__doc__:
            action_doc = action.__doc__.split("\n")[0].strip()
        action_pad = "".join([ " " for x in range(max_len - len(action_name)) ])
        #output.append("%s%s : %s" % (action_name, action_pad, action_doc))
        output.append("%s::" % (action_name))
        output.append(action_doc)
        output.append("")
    with open(outfile, "w+") as f:
        f.write(TEMPLATE % ("\n".join(output)))

