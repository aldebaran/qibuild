## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the doc projects of the given worktree

"""

import operator
import os

import qibuild
import qidoc.core

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.default_parser(parser)
    parser.add_argument("--work-tree", dest="worktree")


def do(args):
    """ Main entry point """
    worktree = args.worktree
    worktree = qidoc.core.find_qidoc_root(worktree)
    if not worktree:
        raise Exception("No qidoc worktree found.\n"
          "Please call qidoc init or go to a qidoc worktree")

    builder = qidoc.core.QiDocBuilder(worktree)

    print "List of qidoc projects in", builder.worktree.root
    print

    print "Doxygen docs:"
    doxydocs = builder.doxydocs.values()
    # Re write the doxydoc.src to be relative to worktree
    for doxydoc in doxydocs:
        doxydoc.src = os.path.relpath(doxydoc.src, builder.worktree.root)
    doxydocs.sort(key=operator.attrgetter("src"))
    for doxydoc in doxydocs:
        print "  ", doxydoc.src
    print

    print "Sphinx docs:"
    sphinxdocs = builder.sphinxdocs.values()
    # Re write the sphinxdoc.src to be relative to worktree
    for sphinxdoc in sphinxdocs:
        sphinxdoc.src = os.path.relpath(sphinxdoc.src, builder.worktree.root)
    sphinxdocs.sort(key=operator.attrgetter("src"))
    for sphinxdoc in sphinxdocs:
        print "  ", sphinxdoc.src
