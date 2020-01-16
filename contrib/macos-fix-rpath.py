#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" usage: fix-rpath.py CROSS_ROOTPATH LIBDIR """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import re
import sys
import stat
import shutil
import subprocess

_dryrun = False

_FILE_EXEC = r'.*?:\s+Mach-O 64-bit (dynamically linked shared library|executable) x86_64'
re_FILE_EXEC = re.compile(_FILE_EXEC)
_LIB_OPT = r'\s*(/opt/.*?\.dylib).*'
re_LIB_OPT = re.compile(_LIB_OPT)


def find_exec(root, maxdepth=None):
    """ Find Exec """
    print("Scanning {0} (maxdepth: {1})".format(root, maxdepth))
    exec_list = list()
    for root_, _, files in os.walk(root):
        for file_ in files:
            file_path = os.path.join(root_, file_)
            p = subprocess.Popen(["file", file_path], stdout=subprocess.PIPE)
            if re_FILE_EXEC.match(p.communicate()[0]) is not None:
                exec_list.append(file_path)
        depth = len(os.path.relpath(root_, root).split(os.sep))
        if maxdepth is not None and depth >= maxdepth:
            break
    return exec_list


def get_wrong_rpath(file_path):
    """ Get Wrong RPath """
    lib_list = list()
    p = subprocess.Popen(["otool", "-L", file_path], stdout=subprocess.PIPE)
    output = p.communicate()[0]
    for line in output.split('\n'):
        m = re_LIB_OPT.match(line)
        if m is not None:
            lib_list.append(m.group(1))
    return lib_list


def fix_rpath(file_path, old_rpath_list, new_libdir):
    """ Fix RPath """
    to_recheck = 0
    cmd = ["install_name_tool"]
    for old_rpath in old_rpath_list:
        lib_file = os.path.basename(old_rpath)
        lib_path = os.path.join(new_libdir, lib_file)
        if not os.path.exists(lib_path):
            print "copying {0} into {1}".format(old_rpath, lib_path)
            dir_stat = os.stat(new_libdir).st_mode
            os.chmod(new_libdir, dir_stat | stat.S_IWRITE)
            shutil.copy(old_rpath, new_libdir)
            rpath = "@executable_path/{0}".format(lib_file)
            cmd_ = ["install_name_tool", "-id", rpath, "-change", old_rpath, rpath, lib_path]
            print "running: {0}".format(" ".join(cmd_))
            p = subprocess.check_call(cmd_)
            os.chmod(new_libdir, dir_stat)
            to_recheck += 1
        rel_path = os.path.relpath(lib_path, file_path)
        if os.path.dirname(file_path) == new_libdir:
            rel_path = lib_file
        new_rpath = "@executable_path/{0}".format(rel_path)
        cmd_opts = list()
        if file_path == lib_path:
            cmd_opts += ["-id", new_rpath]
        cmd_opts += ["-change", old_rpath, new_rpath]
        cmd.extend(cmd_opts)
    cmd.append(file_path)
    if len(cmd) < 3:
        return to_recheck
    print "running: {0}".format(" ".join(cmd))
    if not _dryrun:
        file_stat = os.stat(file_path).st_mode
        os.chmod(file_path, file_stat | stat.S_IWRITE)
        p = subprocess.check_call(cmd)
        os.chmod(file_path, file_stat)
    return to_recheck


def main(root, new_libdir):
    """ Main Entry Point """
    to_recheck = 0
    exec_list = find_exec(root)
    for exec_ in exec_list:
        lib_list = get_wrong_rpath(exec_)
        to_recheck += fix_rpath(exec_, lib_list, new_libdir)
    while to_recheck > 0:
        print "Need to checking {0} for {1} item(s)".format(new_libdir, to_recheck)
        to_recheck = 0
        exec_list = find_exec(new_libdir, 1)
        print "need fix:", exec_list
        for exec_ in exec_list:
            lib_list = get_wrong_rpath(exec_)
            to_recheck += fix_rpath(exec_, lib_list, new_libdir)
    return


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
        mess = "Not enough argument"
        raise Exception(mess)
    cc_root = os.path.abspath(sys.argv[1])
    libdir = os.path.abspath(sys.argv[2])
    main(cc_root, libdir)
