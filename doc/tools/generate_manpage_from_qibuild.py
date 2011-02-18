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

def generate_man(src, dst, packages):
    outfile = sys.argv[1]
    actions = list()
    actions.extend(qitools.cmdparse.action_modules_from_package(packages))

    with open(src, "r+") as f:
        template = f.read()

    max_len = 0
    for action in actions:
        action_len = len(action.__name__[len(packages) + 1:].strip())
        if action_len > max_len:
            max_len = action_len

    output = list()
    for action in actions:
        action_doc = "TODO: documentation"
        action_name = action.__name__[len(packages) + 1:].strip().replace(".", " ")
        if action.__doc__:
            action_doc = " ".join([ x.strip() for x in action.__doc__.split("\n") ])
        action_pad = "".join([ " " for x in range(max_len - len(action_name)) ])
        #output.append("%s%s : %s" % (action_name, action_pad, action_doc))
        output.append("%s::" % (action_name))
        output.append(action_doc)
        output.append("")

    with open(dst, "w+") as f:
        f.write(template % "\n".join(output))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage ./generate_man tpl output package"
        exit(1)

    generate_man(sys.argv[1], sys.argv[2], sys.argv[3])
