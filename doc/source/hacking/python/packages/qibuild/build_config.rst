qibuild.build_config
=====================

.. py:module:: qibuild.build_config

CMakeBuildConfig
-----------------

.. autoclass:: CMakeBuildConfig
    :members:

    .. py:attribute:: profiles

        A list of build profiles to use
        (coming from ``qibuild configure -p<profile>``), or
        read form the local settings

    .. py:attribute:: user_flags

        Additional list of CMake flags
        (comming from ``qibuild configure -D<flags>``)
