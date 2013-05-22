qibuild.profile -- Managing build profiles
==========================================

.. automodule:: qibuild.profile

Profile
--------

.. autoclass:: Profile
    :members:

    .. py:attribute:: name

    .. py:attribute:: cmake_flags

        A list of tuples (name, value)
        (Not a dict because the order matters)


Other functions in this module
------------------------------

.. autofunction:: get_cmake_flags

.. autofunction:: configure_build_profile

.. autofunction:: remove_build_profile

.. autofunction:: parse_profiles



