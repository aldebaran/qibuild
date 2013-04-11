#!/usr/bin/env python

## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Convert an old qibuild.cfg file to a new qibuild.xml file

"""

import sys
import os

# sys.path
def patch_sys_path():
    """
    Add self sources to sys.path, so that directly using this script
    from the sources works

    """
    this_dir = os.path.dirname(__file__)
    to_add =  os.path.join(this_dir, "../python/")
    to_add = os.path.abspath(to_add)
    sys.path.insert(0, to_add)


patch_sys_path()


import argparse

import qisys.script
import qibuild.config


def main():
    """ Main entry poing """

    parser = argparse.ArgumentParser()
    parser.add_argument("cfg_path")
    args = parser.parse_args()
    cfg_path = args.cfg_path
    new_conf = qibuild.config.convert_qibuild_cfg(cfg_path)
    new_cfg = cfg_path.replace(".cfg", ".xml")
    with open(new_cfg, "w") as fp:
        fp.write(new_conf)
    print "New confg written in", new_cfg


if __name__ == "__main__":
    main()
