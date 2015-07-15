qiBuild Install
===============

Dependencies
-------------

Required:

* ``Python2`` with ``setuptools``

Optional:

* ``cmake`` for ``qibuild``
* ``doxygen`` and ``Sphinx`` for ``qidoc``
* ``gettext`` or ``qtlinguist`` for ``qilinguist``
* ``git`` for ``qisrc``
* ``virtualenv`` for ``qipy``


Getting the last stable release
--------------------------------

This is the preferred way.

Install `pip <http://www.pip-installer.org>`_ and then run::

  pip install qibuild

On Windows, make sure ``c:\Python27`` and ``c:\Python27\scripts`` are in ``%PATH%``
(adapt these paths to reflect your Python's installation)

On Linux and Mac, you may want to add ``--user`` in order to not
"pollute" your system.

If you want to be able to use ``qicd``, patch your ``~/.profile`` or
equivalent with::

  function qicd {
    p=$(python -m 'qicd' $1)
    if [[ $? -ne 0 ]]; then
      return
    fi
    cd ${p}
  }


Using the git repository
-------------------------

Create a `virtualenv <https://www.virtualenv.org/en/latest/>`_ and use
the ``--editable`` option of pip::

  virtualenv qibuild-env
  source qibuild-env/bin/activate
  cd /path/to/qibuild
  pip install -e .   # note the dot at the end


Packaging qibuild
-----------------

Just use ``setup.py`` as usual.

Not that qibuild's CMake files will be installed to ``<prefix>/share/cmake``,
regardless of the platform.

If you are packaging for Linux, you may want to:
 * generate and install the man pages (using ``rst2man`` and the files in ``doc/source/man/``)
 * install ``etc/qibuild.sh`` to ``/etc/profile.d`` or similar so that ``qicd`` becomes
   available

