qitest.result -- Storing the result of a test
=============================================

.. automodule:: qitest.result

TestResult
----------

.. autoclass:: TestResult

    .. py:attribute:: test

        A dictionary representing the test, as returned by
        :py:func:`qitest.conf.parse_tests`


    .. py:attribute:: time

        The time in seconds that the test took to run

    .. py:attribute:: ok

        A boolean indicating whether the test was successful

    .. py:attribute:: message

       A list of arguments for a :py:func:`qisys.ui.info` call.
       Used by the :py:class:`.TestLogger`
