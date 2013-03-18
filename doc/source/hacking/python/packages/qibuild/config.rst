qibuild.config -- Managing qiBuild config files
===============================================

.. py:module:: qibuild.config

Read and write qibuild XML configuration files

See
 * :ref:`qibuild-xml-syntax`
 * :ref:`qiproject-xml-syntax`

qibuild.config.QiBuildConfig
-----------------------------

A class to represent qibuild XML configuration


Typical usage is:

.. code-block:: python

   qibuild_cfg = QiBuildConfig()
   qibuild_cfg.read()
   qibuild_cfg.read_local_config(".qi/qibuild.xml")

   # Then every config key is usable using objects
   # or dictionnaries:
   build_dir = qibuild_cfg.local.build.build_dir,
   win32_config = qibuild_cfg.configs['win32-vs2010']
   cmake_generator = win32_config.cmake.generator

   ide = IDE()
   ide.name = "QtCreator"
   ide.path = "/path/to/qtcreator"
   qibuild_cfg.add_ide(ide)

   qibuild_cfg.write()

   qibuild_cfg.local.defaults = "win32-vs2010"

   # save defaults in local xml file:
   qibuild_cfg.write_local_config()


.. autoclass:: qibuild.config.QiBuildConfig
   :members:


