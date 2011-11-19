qibuild.configstore -- Parsing config files
===========================================

.. py:module:: qibuild.configstore

ConfigStore object look very similar to ConfigParser objects.
(and in fact ConfigParser is used for the implementation of ConfigStore)


There are a few differences though.

* The contents of the file are put in a nested ``dict``
  structures, instead of splitting between ``section`` and ``options``

* Instead of using ``section``, and ``option``, you must use
  a dot-separated key name.

For instance a ``example.cfg`` file looking like:

.. code-block:: ini

   [project foo]
   spam = 42

   [project bar]
   eggs = 2

Can be used like this:

.. code-block:: python

   config = qibuild.configstore.ConfigStore()
   config.read("example.cfg")

   spam = config.get("project.foo.spam")
   eggs = config.get("project")

   projects_config = config.get("project")
   for (project, config) in projects_config.iteritems():
      print project, config


qibuild.configstore.ConfigStore
--------------------------------


.. py:class:: ConfigStore

   .. py:method:: get(key[, default=None)

      Get a value from a dot-separated key.
      If the key does not exsist, returns ``default``

   .. py:method:: read(filename)

      Read configuration from filename.


Other functions in this module
------------------------------

qibuild.configstore.update_config
+++++++++++++++++++++++++++++++++


.. py:function:: update_config(config_path, section, key, value)

    Update a config file

    For instance, if ``foo.cfg`` is empty,

    After `update_config_section(foo.cfg, "bar", "baz", "buzz")`:

    ``foo.cfg`` looks like:

    .. code-block:: ini

        [bar]
        baz = buzz

    Note: all comments in the file will be lost!
    Sections will be created if they do not exist.

    Gotcha: this does NOT update a configstore object per se,
    because the configstore may have read several files.

    Here you are just fixing *one* config file, that someone
    else will read later.

    If you want to permanetely store Toc configuration, use
    toc.update_config() instead.

    If value is a list, we will write a string separated by spaces
