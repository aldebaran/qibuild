## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module provides the abstract BinaryPackage class, which should be
inherited when implementing additional binary package supports.

qiBuild toolchains contain a set of packages, which can be extended.

This module provides utility functions to import binary packages used by some
distribution into any qiBuild toolchain.

All qiBuild packages should have the same layout.
"""

import pprint
import types

class BinaryPackageException(Exception):
    """Just a custom exception

    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        message = "Binary package exception:\n"
        message += self._message
        return message

class BinaryPackage:
    """ A binary package is the endpoint of a binary package file provided by
    most of the Linux distribution.

    It stores metadata read from the binary package itself.

    """
    def __init__(self, package_type, package_path):
        self.type     = package_type
        self.path     = package_path
        self.metadata = None

    def get_metadata(self):
        """ Return the metadata.

        If the metadata has not been cached yet, then it is read/laoded and
        cached in the instance.

        The metadata is stored in a dictionary, which has the following layout:

          metadata = {
            name,
            version,
            revision,
            arch,
            arch_variant,
            dependencies = {
              buidtime,
              runtime,
              post-install,
              all,
            },
          }

        :return: the metadata dictionary

        """
        raise NotImplementedError()

    def extract(self, dest_dir):
        """ Extract the binary package content, without the metadata.

        :param dest_dir: the extraction directory

        :return: the root directory of the extracted content

        """
        raise NotImplementedError()

    def __str__(self):
        res = "Binary package:\n"
        res += '  Type: {0}\n'.format(self.type)
        res += '  Path: {0}\n'.format(self.path)
        res += '  Metadata:\n'
        res += pprint.pformat(self.metadata, indent=2)
        return res
