qitoolchain.binary_package.gentoo_portage -- Toolchain binary packages Gentoo (with portage dependency)
=======================================================================================================

.. py:module:: qitoolchain.binary_package.gentoo_portage

This module implements the Gentoo binary packages class, which takes benefit
from *portage* modules.

This module depends on *portage*: http://www.gentoo.org/proj/en/portage/index.xml

.. py:class:: GentooPackage(package_path)

  This class is to represent a Gentoo binary package endpoint using ``portage``.

  .. py:method:: extract(dest_dir)

    Extract the binary package content, without the metadata, into the
    ``dest_dir``.

    :param dest_dir: the extraction directory

    :rtype: the root directory of the extracted content

  .. py:method:: get_metadata()

    Read the metadata from the binary package and store them in the instance.

    :rtype: the metadata dictionary
