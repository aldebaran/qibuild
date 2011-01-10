#!/usr/bin/env python
##
## Author(s):
##  -  <>
##
## (is it fantomas?)
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

#fold into actions, generate an asciidoc manpage
import sys
import qitools.cmdparse

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

CONFIGURATION
-------------
The configuration file is stored in .qi/build.cfg. +
The following keys are available:

General::

general.build.config:::
    The default build configuration. (see Build)

general.cmake.flags:::
    Additional cmake flags to pass to all projects, in all configuration.
    If you want specific clags for a configuration, please refer to Build.
    Flags look like: "FOO=BAR TITI=CACA"

Project::
Configuration specific to a project.

*project.<name>.cmake.flags*:::
    like general.cmake.flags but applied to a specific project.

project.<name>.depends:::
    specify the depends that apply to a project, this is only build depends.
    this is a space separated list.

project.<name>.rdepends:::
    specify runtime dependencies of a project.
    this is a space separated list.


Build::
This section allow creating specific build configuration.
You set the default build configuration using general.build.config.
You can pass the build configuration using -c <buildconfig> in command line.

build.<name>.cmake.flags:::
   cmake flags specific to a build configuration.


Toolchain::
Toolchain specific configuration.

toolchain.<name>.provide:::
    Name of projects that should not be build but instead taken from the toolchain.

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
    actions.extend(qitools.cmdparse.action_modules_from_package("qibuild.actions"))

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

