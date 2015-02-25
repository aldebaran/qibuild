## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Tools for doxygen """

import os
import collections

def read_doxyfile(doxyfile):
    """ Parse a doxyfile path.

    :returns: a dict key, value containing
              the settings if the doxyfile exists,
              else an empty dict

    """
    res = collections.OrderedDict()
    if not os.path.exists(doxyfile):
        return res
    with open(doxyfile, "r") as fp:
        lines = fp.readlines()

    # Handle lines ending with backshlash
    contents = ""
    for line in lines:
        if line.endswith("\\\n"):
            contents += line.strip()[:-1]
        else:
            contents += line

    lines = contents.splitlines()
    for line in lines:
        if line.startswith("#"):
            continue
        if "+=" in line:
            key, value = line.split("+=", 1)
            previous_value = res.get(key.strip())
            if not previous_value:
                mess = "Error when parsing Doxyfile in " + doxyfile + "\n"
                mess += line + "\n"
                mess += "does not match any assignment"
                raise Exception(mess)
            res[key.strip()] += " " + value.strip()
        elif "=" in line:
            key,  value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            res[key] = value

    return res

def write_doxyfile(config, doxyfile):
    """ Write a doxyfile """
    with open(doxyfile, "w") as fp:
        for key, value in config.iteritems():
            fp.write("%s = %s\n" % (key, value))
