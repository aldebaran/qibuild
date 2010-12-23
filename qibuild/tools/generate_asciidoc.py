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

import qibuild.shell

if __name__ == "__main__":
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
    print """\
QIBUILD(1)
==========
:doctype: manpage


NAME
----
qibuild - get, build, install projects.


SYNOPSIS
--------
*qibuild* ['OPTIONS'] COMMAND ['COMMAND_OPTIONS'] ARGUMENTS


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


DESCRIPTION
-----------
The command line program toc provide severals actions to work with projects.


COMMAND
-------
%s


EXIT STATUS
-----------
*0*::
    Success

*1*::
    Failure


BUGS
----
    th3r3 15 n0 5p00n

""" % ("\n".join(output))
