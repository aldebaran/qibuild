""" Make all python projects available in the current build configuartion

"""
import sys
import os

from qisys import ui
import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree

def configure_parser(parser):
    qibuild.parsers.build_parser(parser)
    # FIXME: add -r
    parser.add_argument("requirements", nargs="*")

def do(args):
    python_builder = qipy.parsers.get_python_builder(args)
    python_builder.configure()
