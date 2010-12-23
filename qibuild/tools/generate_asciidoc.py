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
    actions.extend(qibuild.shell.main.action_modules_from_package("qibuild.actions.qibuild"))
    actions.extend(qibuild.shell.main.action_modules_from_package("qibuild.actions.toc"))

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
    print """
TOC(1)
======
:doctype: manpage


NAME
----
toc - get, build, install projects.


SYNOPSIS
--------
*toc* ['OPTIONS'] COMMAND ['COMMAND_OPTIONS'] ARGUMENTS


DESCRIPTION
-----------
The command line program toc provide severals actions to work with projects.

COMMAND
-------
TODO: move inside command?
Commands bellow allow building a project and it's dependencies.
If a binary archive of a depedencies is available, specified projects
will build using them.

*toc configure* - configure a project using qibuild
*toc build* - build a project using qibuild

Command bellow always works on all buildable projects.
*toc foreach
*toc pull*
*toc push*

COMMANDS
--------
%s

OPTIONS
-------
*-b, --backend*='BACKEND'::
    Backend output file format: 'docbook45', 'xhtml11', 'html4',
    'wordpress' or 'latex' (the 'latex' backend is experimental).
    You can also the backend alias names 'html' (aliased to 'xhtml11')
    or 'docbook' (aliased to 'docbook45').
    Defaults to 'html'.

*-f, --conf-file*='CONF_FILE'::
    Use configuration file 'CONF_FILE'.Configuration files processed
    in command-line order (after implicit configuration files).  This
    option may be specified more than once.

*-h, --help*[='TOPIC']::
    Print help TOPIC. *--help*='topics' will print a list of help
    topics, *--help*='syntax' summarizes AsciiDoc syntax,
    *--help*='manpage' prints the AsciiDoc manpage.

*-v, --verbose*::
    Verbosely print processing information and configuration file
    checks to stderr.

*--version*::
    Print program version number.


EXIT STATUS
-----------
*0*::
    Success

*1*::
    Failure

BUGS
----
    f@r @ct|@n |n @ct|@ns:
        pr|nt "==== ===="
        pr|nt "d@c:", @ct|@n.__n@me__, ": ", @ct|@n.__d@c__

""" % ("\n".join(output))
