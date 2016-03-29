## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Set of tools related to version numbers

"""

import re
import packaging.version

def compare(a_str, b_str):
    """ Compare two versions

    >>> compare("1.2.3", "1.2.3")
    0
    >>> compare("1.2.3", "1.2.3-rc1")
    1
    >>> compare("1.20", "1.3")
    1
    >>> compare("1.20", "1.3-rc2")
    1

    """
    version_a = packaging.version.parse(a_str)
    version_b = packaging.version.parse(b_str)
    if version_a == version_b:
        return 0
    if version_a > version_b:
        return 1
    if version_a < version_b:
        return -1

def increment(version):
    """
    >>> increment("0.0.3")
    '0.0.4'
    >>> increment("2.4-rc1")
    '2.4-rc2'
    >>> increment("2.4-alpha")
    Traceback (most recent call last):
        ...
    ValueError: version must end with a digit

    """
    match = re.search("\d+$", version)
    if match is None:
        raise ValueError("version must end with a digit")
    as_int = int(match.group())
    as_int += 1
    return re.sub("\d+$", str(as_int), version)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
