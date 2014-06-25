""" Generate a -config.cmake file from the contents of a directory """

from qisys import ui
import qisys.parsers
import qibuild.cmake.modules

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("directory")
    parser.add_argument("--name", required=True)

def do(args):
    directory = args.directory
    name = args.name
    res = qibuild.cmake.modules.generate_cmake_module(directory, name)
    ui.info(ui.green, "CMake module generated in", ui.reset, ui.bold, res)
