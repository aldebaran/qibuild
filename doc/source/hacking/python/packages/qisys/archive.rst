qisys.archive -- Manage .tar.gz and .zip files
==============================================

.. automodule:: qisys.archive
   :members:

.. autofunction:: compress

.. autofunction:: extract

    If the content is archiving relatively to "." or "/", then this leading
    field of the path is replace by the archive name.

    If several directories or files are stored at the root of the archive, then
    they will be extracted in a directory maned using  the archive name.

    e.g.:

    * Wrong leading field in pathes:

      * Archive content::

          ./foo
          ./foo/bar
          ./foo/bar/bar.txt
          ./foo/baz.txt

      * Extacted location::

          directory/archive_name/foo
          directory/archive_name/foo/bar
          directory/archive_name/foo/bar/bar.txt
          directory/archive_name/foo/baz.txt

    * Several items at the root of the archive:

      * Archive content::

          foo
          foo/bar
          foo/bar/bar.txt
          baz.txt

      * Extacted location::

          directory/archive_name/foo
          directory/archive_name/foo/bar
          directory/archive_name/foo/bar/bar.txt
          directory/archive_name/baz.txt

.. autofunction:: guess_algo
