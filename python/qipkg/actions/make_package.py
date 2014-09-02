## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """

from qisys import ui
import qisys.parsers
import qipkg.parsers
import qipkg.metapackage
import qipkg.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("-o", "--output")
    parser.add_argument("--with-breakpad", action="store_true")
    parser.set_defaults(with_breakpad=False)


def do(args):
    """Main entry point"""
    output = args.output
    with_breakpad = args.with_breakpad
    worktree = qisys.parsers.get_worktree(args)
    pml_builders = qipkg.parsers.get_pml_builders(args)
    all_packages = list()
    ui.info("\n", ui.green, "::", ui.reset, ui.bold,
            "Building", len(pml_builders), "package(s)\n")
    for i, pml_builder in enumerate(pml_builders):
        ui.info(ui.green, "::", ui.reset,
                ui.bold, "[%i on %i]" % (i + 1, len(pml_builders)),
                ui.reset, ui.blue, pml_builder.pml_path)
        packages = pml_builder.make_package(output=output, with_breakpad=with_breakpad)
        all_packages.extend(packages)
    if args.pml_path.endswith(".pml"):
        return all_packages
    else:
        meta_package = qipkg.metapackage.MetaPackage(worktree, args.pml_path)
        return meta_package.make_meta_package(all_packages)
