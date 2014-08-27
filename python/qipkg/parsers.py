## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """
import copy

import qisys.parsers
import qipkg.builder

import qibuild.parsers
import qipy.parsers
import qilinguist.parsers
import qipkg.metapackage


def pml_parser(parser):
    qisys.parsers.build_parser(parser)
    parser.add_argument("pml_path")

def get_pml_builder(args):
    pml_path = args.pml_path
    worktree = qisys.parsers.get_worktree(args)
    build_worktree = qibuild.parsers.get_build_worktree(args)
    # Note that we do not use the get_*_builders because we will not
    # read the projects from the command line.
    # Instead the projects attribute of each builder will be set
    # in PMLBuilder.__init__()
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    cmake_builder.projects = list()
    python_builder = qipy.parsers.get_python_builder(args, verbose=False)
    python_builder.projects = list()
    linguist_builder = qilinguist.parsers.get_linguist_builder(args,
            with_projects=False)
    linguist_builder.projects = list()
    return qipkg.builder.PMLBuilder(pml_path, cmake_builder,
                                    python_builder, linguist_builder)

def get_pml_builders(args):
    res = list()
    if args.pml_path.endswith(".mpml"):
        metapackage = qipkg.metapackage.MetaPackage(args.pml_path)
        for pml_path in metapackage.pml_paths:
            new_args = copy.copy(args)
            new_args.pml_path = pml_path
            res.append(get_pml_builder(new_args))
    else:
        res.append(get_pml_builder(args))
    return res
