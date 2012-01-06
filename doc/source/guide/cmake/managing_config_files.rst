.. _cmake-config-files:

Managing configuration files
============================

Let's assume the foo executable needs to read a config file named ``foo.cfg``

You may want to:

* Put ``foo.cfg`` into version control

* Configure ``foo.cfg`` with CMake (maybe the contents of foo.cfg depends on wether
  you are on windows or on linux ...)

Also, it could be convenient if there was a unique way for the foo executable
to find foo.cfg.

A possible solution is to make sure you always have the following layout::

  <prefix>
  |__ bin
      |__ foo
      etc
      |__ foo
          |__ foo.cfg

And then, to find ``foo.cfg,`` you just have to use ``argv[0]`` and it always work,
whereas you just have built ``foo``, or if is installed.

One way to achieve this with CMake would be to use something like this:
(assuming that ``foo.cfg`` is in ``foo/foo.cfg``)

.. code-block:: cmake

  qi_create_bin(foo main.cpp)

  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/foo.cfg
    ${QI_SDK_DIR}/${QI_SDK_CONF}/foo/foo.cfg
    COPY_ONLY)

  qi_install_conf(foo.cfg SUBFOLDER foo)

Right before starting to build, the ``foo.cfg`` will be copied by CMake using
``configure_file`` into the correct location, and then you can add an install rule
to install the file to the correct location.
