# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" List the contents of a package """

import zipfile
import os
import tabulate

from qisys import ui
import qisys.parsers


def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")
    parser.add_argument("--sort", "-s", default="f", action="store")
    parser.add_argument("--reverse", "-r", action="store_true")
    parser.add_argument("--parseable", "-p", action="store_true")


def human_size(n):
    prefixes = ['', 'k', 'M', 'G', 'T', 'P']
    p = 0
    while n >= 1024 and p < len(prefixes):
        p += 1
        n /= 1024
    return "%u%sB" % (round(n), prefixes[p])


def build_list(pkgname):
    with zipfile.ZipFile(pkgname, "r") as pkg:
        def get_entry(f):
            info = pkg.getinfo(f)
            return [info.filename, info.file_size, info.compress_size]
        return map(get_entry, pkg.namelist())


def ls_package(pkgname, sort="f", reverse=False, parseable=False):
    filelist = build_list(pkgname)
    s = {'f': 0, 's': 1, 'c': 2}
    filelist = sorted(filelist, key=lambda f: f[s[sort]], reverse=reverse)

    ui.info("%s" % pkgname)
    ui.info("%d files" % len(filelist))
    ui.info("%s compressed" % human_size(os.path.getsize(pkgname)))
    ui.info("%s uncompressed\n" % human_size(sum([f[1] for f in filelist])))
    ui.info(filelist if parseable
            else tabulate.tabulate(filelist, headers=["File", "Size", "Cmpr"]))


def do(args):
    ls_package(args.pkg_path,
               sort=args.sort,
               reverse=args.reverse,
               parseable=args.parseable)
