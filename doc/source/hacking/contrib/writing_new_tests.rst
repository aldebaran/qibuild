.. _qibuild-writing-tests:

Writing new tests
==================

This section contains a few recipes to help you adding new tests
to the existing code base.

.. warning:: Most of the tests you will see in qiBuild source code
            were written a long time ago and do not follow these guidelines.


qiBuild code base is somewhat hard to test for several reasons.

It's a build framework, so there are lots of code which interact
with the operating system.

More specifically

* The code essentially consists in calling commands with the correct arguments
* Lots of code relies on the file system (to read the configuration file, to
  write generated CMake code and so on)
* Some code is platform-dependent

Here are a few guide lines which should help you overcome these issues
and writing new tests.


Use py.test
-----------

Do NOT use ``unittest`` to write new tests.

* It depends on the stdlib, so it means you can have trouble when testing for
  Python2.6, for instance

* It forces you to put the code in classes, which is not a very Pythonic
  way of doing things

Use `py.test <http://pytest.org>`_ instead

Guide lines
+++++++++++

* Put the code for ``mypackage.mymodule`` in
  ``mypackage/test/test_mymodule.py``

For instance

.. code-block:: python

    # In mypackage/mymodule.py

    def frobnicate(bar=True):
        pass

.. code-block:: python

    # in mypackage/test/test_mymodule.py

    from mypackage.mymodule import frobnicate

    def test_frobnicate():
        res = frobnicate(bar=True)
        assert res is False
        res = frobnicate(bar=False)
        assert res is True

And then you can quick run the frobnicate tests with

.. code-block:: console

    $ py.test2 mypackage/test/test_mymodule.py
    # or:
    $ py.test2 -k frobnicate


Do not put too much code in your action
----------------------------------------

Basically, inside the code of an action, you should just:

* Parse some arguments
* Initialize a few objects
* Call some methods from an other package.


Use dependency injection when possible
--------------------------------------

Generally speaking, the following code is
hard to test:


.. code-block:: python

    class Foo:
        def __init__(self):
            # Reading some config files from the filesystem
            self.config = read_config()

        def do_something(self):
            if self.config.foo_bar:
                do_foo_bar()

    class MyClass():
        def __init__(self):
            self.foo = Foo()

        def frobnicate(self):
            res = self.foo.do_something()
            # Do something with res



If you want to test ``MyClass.frobnicate``, you have to create the resources
used by the ``Foo`` class.

By a simple refactoring, you can make the situation much easier for
you

.. code-block:: python

    class MyClass():
        def __init__(self, foo=None)
            if foo is None:
              self.foo = Foo()
            else:
              self.foo = foo

Then in your test, you can do something like:

.. code-block:: python

    class FakeFoo:
        def __init__(self, res):
            self.res = res
        def do_something():
            return res

    def test_frobnicate():
        fake_foo = FakeFoo(False)
        my_class = MyClass(foo=fake_foo)
        # Do some test with my_class.frobnicate()

.. seealso::

   * `Don't Look For Things <http://www.youtube.com/watch?v=RlfLCWKxHJ0>`_
     Google Tech Talk about this topic (For the Java programming language, but
     most of the talk is transposable to Python)

Testing exceptions
-------------------

Most of qibuild source code use exception as a way
to display error messages to the end users.

.. code-block:: python

     # In the code that is used by every action:

     try:
          module.do()
     except Exception as e:
          ui.error(str(e))


So it's important to check the correctness of
the error message.

This is how to do it:

.. code-block:: python

    import pytest

    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        do_something_that_should_raise()
    assert "Bad input"  in e.value.message


Notes:

* The ``pylint disable-msg`` is necessary because ``pytest``
  uses a "lazy import" mechanism that causes false negative
  when running ``pylint``

* You have to get the original exception with ``e.value.message``
  ``py.test`` automatically rewrites the exceptions that are thrown
  during a test case, and for instance ``str(e)`` is **not** what you
  would expect ...

.. seealso::

  * The :ref:`qibuild-coding-guide-error-messages` section in the
    qibuild coding guide



Testing code that uses the filesystem
-------------------------------------

Easy case: just reading a file
+++++++++++++++++++++++++++++++

If you have some code looking like:

.. code-block:: python

    def read_config(fp):
        """ Parse the config file from the file-like object

        """

You can just use ``StringIO``

.. code-block:: python

    from StringIO import StringIO


    def test_parse_config():
        config_fp = StringIO("\n")
        config = read_config(config_fp)
        # Do something with config

It also works for writing instead of reading, obviously.

Most of the stdlib of Python accepts both file paths
and file-like objects.


Hard case: using temporary directories
+++++++++++++++++++++++++++++++++++++++


In this case you should use the built-in ``tmpdir`` from ``py.test``

.. code-block:: python


   def test_foo(tmpdir)

      work = tmpdir.mkdir("work")
      dot_di = tmpdir.mkdir(".qi")
      qibuild_xml = dot_qi.join("qibuild.xml")
      qibuild_xml.write("....")

      worktree = qisys.worktree.open(work.strpath)


Note that ``tmpdir`` is  a  ``py.._path.local.LocaPath`` instance (from the
``pylib`` project by the same author of ``pytest``)

This is why you have all these beautiful methods available.

``tmpdir`` is a magic function argument that ``py.test`` provides.

You are sure that this directory is created empty, is writeable, and
will be removed at the end of the test.

.. seealso::

   * `py.path.local on readthedocs.org <http://pylib.readthedocs.org/en/latest/path.html#py-path-local-local-file-system-path>`_



Testing code that interacts with the user
-----------------------------------------

Here we introduce an other library called ``mock``.

The idea is that we will dynamically replace a function by
an other.  (This is also called ``monkey-patching``)

There are some tools in ``py.test`` for monkey patching, but the
``mock`` project contains much more features.


.. seealso::

   * `mock documentation <http://www.voidspace.org.uk/python/mock/>`_


Here's how to use it in ``py.test``:

.. code-block:: python

    import mock

    def test_foo():
        with mock.patch('module.fun') as m:
            m.return_value = True
            # From now on module.fun is replaced by a
            # function that always return True

            # do something that uses module.fun

            # You can also write checks using m.called_args
            # here.


Some classes are available for you to be used as mock.

(It's good idea to re-use the same mock for all the tests)

So, here's how you can write code that uses ``qibuild.interact``


.. code-block:: python

    # in foo.py
    import qibuild.interact

    def foo():
        bar = qibuild.interact.ask_yes_no("bar ?")
        spam = qibuild.interact.ask_string("please enter spam value")

.. code-block:: python

    import mock
    from qibuild.test.interact import FakeInteract

    def test_foo():
        fake_interact = FakeInteract([False,  "eggs"])
        with mock.patch('qibuild.interact', fake_interact):
            # Do something that uses qibuild.interact.
            # Everything will happen as is ask_yes_no returned
            # False and ask_string returned "eggs"

Note that you must built the ``FakeInteract`` object with the
*returned* value of the various ``qibuild.interact.ask_`` functions.


If you do not want to use a list, you can use a dictionary instead,
the keys should match parts of the questions that are asked.

.. code-block:: python

    def test_foo():
        fake_interact = FakeInteract({"bar" : False, "spam" : "egges"})


Testing code that compiles source code
--------------------------------------

There are times where you really need a 'real' worktree
and some real source code.

.. todo:: explain how to use the worktree in qibuild/python/qibuild/test
