""" List the contents of a package """

import zipfile
import qisys.parsers

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")

def do(args):
    pkg_path = args.pkg_path
    archive = zipfile.ZipFile(pkg_path)
    for fileinfo in archive.infolist():
        print fileinfo.filename
