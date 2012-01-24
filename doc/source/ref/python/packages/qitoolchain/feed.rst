qitoolchain.feeds -- Parsing toolchain feeds
============================================

.. py:module:: qitoolchain.feed

All the XML parsing is done with the excellent `xml.etree.ElementTree`
standard Python library.


qitoolchain.feed.parse_feed
---------------------------

.. py:function:: parse_feed(toolchain, feed)

    Parse an xml feed, adding packages to the toolchain
    while doing so

    :param toolchain: a
      :py:class:`Toolchain <qitoolchain.toolchain.Toolchain>` instance
    :param feed: a feed location. Maybe a path or an url.

    Create a :py:class:`ToolchainFeedParser` object, then get
    the list of parsed packages, and call :py:func:`handle_package`
    for each package


qitoolchain.feed.ToolchainFeedParser
------------------------------------

.. py:class:: ToolchainFeedParser

   A class to handle feed parsing

   .. py:attribute:: packages

      A list of packages, stored as ``ElementTree`` objects.
      The feed where the package came from is stored in a
      "feed" XML atribute of this package for later use.

    .. py:attribute:: _versions

       A dict name->version used to only keep the latest
       version of packages

    .. py:method::  append_package(package_tree)

        Add a package to self.packages.
        If an older version of the package exists,
        replace it by the new version

    .. py:method:: parse(feed)

       Recursively parse the feeds, filling :py:attr:`packages` while doing so.


Handling packages
-----------------

.. py:function:: handle_package(package, package_tree, toolchain)

    Handle a package.

    :param package:
      a :py:class:`Package <qitoolchain.toolchain.Package>`
      instance.
      Initially the Packge object will only have its name set,
      but after is has been handled, it will have a correct
      ``path`` and a correct ``toolchain_file`` attributes.

    :param package_tree:
      A ``ElementTree`` object. Note that it contains all the
      attribute it had when it was parse from the feed, plus
      a 'feed' attribute containing the url of the feed it
      was parsed from.

    :param toolchain:
      The :py:class:Toolchain <qitoolchain.toolchain.Toolchain>`
      class to which the package will be added.


    Depending on the attribute of the XML object, several
    functions will be called.


.. py:function:: handle_remote_package(package, package_tree, toolchain)

    Set the `path`` attribute of the given package,
    downloading it and extracting it inside
    ``toolchain.cache`` if necessary.


.. py:function:: handle_local_package(package, package_tree)

    Set ``package.path`` using the feed attribute.
    Useful when the package path is relative to the feed

    For instance with:

    .. code-block:: xml

        <!-- in /path/to/sdk/feed.xml -->
        <package name="foo directory="foo" >

    ``package.path`` will be ``/path/to/foo``

.. py:function:: handle_toochain_file(package, package_tree)

    Set ``package.toolchain_file`` using ``package.path``
    The toolchain file path wil always be relative
    to the package path.



Note: this functions are called in precisely that order.

This means that something like:

.. code-block:: xml

    <package
      name="foo-ctc"
      url="http://example.com/packages/foo-ctc.tar.gz"
      toolchain_file="cross-config.cmake"
    />

will work.


.. seealso::

  * You can read about the XML format of feeds in the
    :ref:`toolchain-feed-syntax` section.
  * You can read more about what happens next when using
    `qitoolchain create`, `qibuild configure` in the
    :ref:`parsing-toolchain-feeds` overview

