#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild 3.7 Migration """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import argparse
import ConfigParser

import qitoolchain.toolchain
import qisys.sh
import qisys.qixml
import qisys.parsers
from qisys import ui


def get_old_toolchains():
    """ Return a dict name -> feed from the previous config format """
    res = dict()
    cfg_path = qisys.sh.get_config_path("qi", "toolchains.cfg")
    config = ConfigParser.ConfigParser()
    config.read(cfg_path)
    if not config.has_section("toolchains"):
        return res
    tc_items = config.items("toolchains")
    for name, value in tc_items:
        res[name] = value
    return res


def recreate_toolchains():
    """ Recreate Toolchain """
    old_toolchains = get_old_toolchains()
    old_names = old_toolchains.keys()
    old_names.sort()
    errors = list()
    for i, name in enumerate(old_names):
        ui.info(ui.bold, "[ %d on %d ]" % (i+1, len(old_names)), name)
        feed_url = old_toolchains[name]
        if feed_url:
            toolchain = qitoolchain.toolchain.Toolchain(name)
            try:
                toolchain.update(feed_url=feed_url)
            except Exception as exp:
                errors.append((name, exp))
    if errors:
        ui.error("Could not update some toolchains")
        for name, error in errors:
            ui.error(" * ", name, error)


def main():
    """ Main Entry Point """
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-toolchains", action="store_false", dest="toolchains",
                        help="Do not try to recreate the toolchains")
    parser.add_argument("--no-backup", action="store_false", dest="backup",
                        help="Do not backup build profiles")
    parser.set_defaults(toolchains=True, backup=True)
    qisys.parsers.worktree_parser(parser)
    args = parser.parse_args()
    worktree = qisys.parsers.get_worktree(args)
    ui.info(ui.bold, "Starting 3.7 migration")
    if args.toolchains:
        ui.info(ui.bold, ":: Re-creating toolchains ...")
        recreate_toolchains()
    ui.info(ui.bold, ":: Removing build profiles ...")
    qibuild_xml_path = os.path.join(worktree.dot_qi, "qibuild.xml")
    tree = qisys.qixml.read(qibuild_xml_path)
    root = tree.getroot()
    profiles = tree.find("profiles")
    if profiles is not None:
        if args.backup:
            profiles.tag = "profiles.back"
        else:
            root.remove(profiles)
    qisys.qixml.write(root, qibuild_xml_path)


if __name__ == "__main__":
    main()
