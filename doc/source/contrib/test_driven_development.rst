.. _qibuild-tdd:

qibuild: using test driven development
=======================================

Red, Green, Refactor
--------------------

Test Driven Development is an old technique, but we
found it very effective during the development of qibuild.

To be truly effective, your code must go through three steps:
red, green, refactor

Assuming you want to fix a bug.

First, you write a *failing* test reproducing the bug.

Then, you *change* the code until the test passes.

Then, you *refactor* the code if you need too, making sure that all test pass.



Rationale
---------

Write a failing test first
+++++++++++++++++++++++++++

Having a test that fails at first if a good thing, because you can know the
test is actually testing something, and is not doing a complex version of

.. code-block:: python

   def test_foo(self):
      self.assertTrue(1 == 1)

In case of adding a new features, writing the test first forces you to
think about the testability of the new code you are going to write, which
may seem a waste of time.

But code that is easy to test is easy to change or refactor (see below),
and the fact that the code is testable usually means there is a good
decoupling of concerns, which is also a good thing.

Writing the tests first also makes you think about the specifications of
your new features. If you do not have a clear set of specifications in mind,
your are not going to write good software.

Note that it is perfectly reasonable to also add the specifications in
the qibuild documentation even before writing the tests, that's a good
way to get feedback. It may seem strange to start by writing the
documentation, but we also fint this technique very effective.

Last, but not least, writing the tests first makes you think about the
*interface* of the new code you are going to write, which is also a good thing:
clear and clean API also make for more maintanable code.



Refactor code when done
+++++++++++++++++++++++


We are proud of ``qibuild`` source code, and we want to have the best code
quality as possible.

In order to do that, we never hesitate to:

* do massive refactoring (the Python API is not stable yet at all)
* change the config files format (they are not stable either yet)

An other good thing about TDD is that is also tells you when to just
stop coding, thus preventing feature creep.

If you started by adding specifications in the documentation, you know what you
are doing, you had no problem writing the test cases, and as soon as all the tests
pass, you know you can stop coding.


Links
-----

* `Chapter about unit testing from the "Dive Into Python book"
  <http://www.diveintopython.net/unit_testing/diving_in.html>`_
* `What Killed Smalltalk Could Kill Ruby, too
  <http://www.youtube.com/watch?v=YX3iRjKj7C0>`_
  (A fasinating talk by Robert Martin at RailsConf 09, about programming in general,
  with a focus on unit testing at the end)
* `Fast Test, Slow Test <https://www.youtube.com/watch?v=RAxiiRPHS9k>`_
  A talk by Gary Bernhardt at PyCon 2012

.. seealso::

   * :ref:`qibuild-test-suite`
   * :ref:`qibuild-writing-tests`
