qibuild.test.test_interact
==========================

.. py:module:: qibuild.test.test_interact

FakeInteract mock object
-------------------------

.. autoclass:: FakeInteract
   :members:

A class to be used as a mock for the functions of
the :py:mod:`qibuild.interact` module


Example:

Let's assume you have a function called ``serve_breakfast``
looking like:

.. code-block:: python

   import qibuild.interact

   def serve_breakfast():
        """ Ask the user if we want coffee or tead,
        and then bring him the breakfast

        """

        coffee = qibuild.interact.ask_yes_no("Do you want coffee ?")
        if coffee:
            serve_coffee()
        else:
            serve_tea()


And you want to test this code.

Well, it's not easy because it depends on a what the user enters,
so how do you run automatic tests with that ?

The idea is to use a mock object for  this:

.. code-block:: python


   import mock
   from qibuild.test.test_interact import FakeInteract


   def test_serve_breakfast():
        fake_interact = FakeInteract([True])
        with mock.patch('qibuild.interact', fake_interact):
            # Every called to `qibuild.interact.ask_*` will be replaced
            # by fake_interact.get_answer()
            # do something with serve_breakfast(), we know that
            # serve_coffee() will be called here
      # now you can use qibuild.interact as normal
