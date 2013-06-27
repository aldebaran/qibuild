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

    for line in lines:
        if line.startswith("#"):
            continue
        if "=" in line:
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


