Python coding guide
===================

.. highlight:: python

General
-------

Pure coding style
^^^^^^^^^^^^^^^^^

The code should follow the Python coding style expressed in
`PEP8 <http://www.python.org/dev/peps/pep-0008/>`_ with the following
exceptions:

* Soft limit for line length is 80 characters. Hard limit is 100 characters.
  You should only exceed 80 characters if it doesn't hurt readability.

* Indentation is made of *four spaces*. No exception.

* No trailing whitespace are allowed.

* Every text file must be pushed using *UNIX line endings*. (On windows, you
  are advised to set ``core.autocrlf`` to true).

* Please use a spell checker when you write comments. Typos in comments are
  annoying and distractive, typos in doc strings are bad because we generate
  public documentation from some of those doc strings.

* There must be two lines between top-level definitions. One line between
  methods.

* The `Google Python Style Guide <http://google-styleguide.googlecode.com/svn/trunk/pyguide.html>`_
  and `Pocoo Team Style Guide <http://www.pocoo.org/internal/styleguide/#styleguide>`_
  contain lots of useful things, please read them.

Use the standard library
^^^^^^^^^^^^^^^^^^^^^^^^^

There are lots of good modules in the Python standard library. Please have a
look here before re-inventing the wheel.

Use built-in types a maximum.

Some examples of useful `built-in functions <http://docs.python.org/2/library/functions.html>`_:

* `range <http://docs.python.org/2/library/functions.html#range>`_ to generate
  a list (range).

* `min <http://docs.python.org/2/library/functions.html#min>`_ and
  `max <http://docs.python.org/2/library/functions.html#max>`_ instead of
  writing a loop to compute the lowest/biggest element of the list.

* `enumerate <http://docs.python.org/2/library/functions.html#enumerate>`_,
  `reversed <http://docs.python.org/2/library/functions.html#reversed>`_ and
  `sorted <http://docs.python.org/2/library/functions.html#sorted>`_ for list
  manipulation.

Some examples of useful `modules <http://docs.python.org/library/>`_:

* `argparse <http://docs.python.org/2/library/argparse.html>`_ for command line
  arguments parsing.

* `itertools <http://docs.python.org/library/itertools.html>`_ instead of writing
  for loops.

* `pprint <http://docs.python.org/library/pprint.html>`_, instead of trying to
  rewrite complex ``__str__`` functions

* `re <http://docs.python.org/2/library/re.html>`_ for regular expression
  operations.

Some string functions you will always use:

* `startswith <http://docs.python.org/2/library/stdtypes.html#str.startswith>`_
  and `endswith <http://docs.python.org/2/library/stdtypes.html#str.endswith>`_
  instead of ``foo[:5] == 'aldeb'``.

* `join <http://docs.python.org/2/library/stdtypes.html#str.join>`_,
  `split <http://docs.python.org/2/library/stdtypes.html#str.split>`_ and
  `splitlines <http://docs.python.org/2/library/stdtypes.html#str.splitlines>`_
  to join multiple strings with the same separator or split a string into a
  list on a separator.

* `ljust <http://docs.python.org/2/library/stdtypes.html#str.ljust>`_ and
  `rjust <http://docs.python.org/2/library/stdtypes.html#str.rjust>`_
  instead of writing custom padding code

* Always precise object when creating it. Use `foo = list()` instead of `foo = []`.
  `bar = set()` instead of `bar = {}`, etc.

* You can compute max/min/join on any iterator, so no need to create a list, a generator is enough:
  `max(len(x) for x in myiterable)`

Some more specific rules
------------------------

Do not just copy/paste code from the Internet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's perfectly fine to look on the Internet for a solution of your problem. If
you find a snippet of code you want to copy/paste, please:

* check the license if any (qiBuild must stay BSD compatible, so no GPL code)
* fix the style if necessary
* cite the origin of your code and their authors, either in a comment, or for
  bigger code, in the README.rst

Always specify optional arguments explicitly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you have a function that looks like this:

.. code-block:: python

    def foo(project, config=None):
        """run foo on the given project"""

Python will let you use ``foo(my_proj, "linux32")``, automatically converting
the regular argument ``linux32`` into the optional argument named ``config``

Please don't do that and use the explicit form instead:

.. code-block:: python

    # in bar.py

    # BAD : second argument is in fact an optional argument.
    foo(my_proj, "linux32")

    # OK: the optional argument is explicit:
    foo(my_proj, config="linux32")

This can cause problems if someone ever changes the ``foo`` function and adds a
new optional argument *before* ``config``:

.. code-block:: python

    def foo(project, clean=False, config=None):
        """run foo on the given project

        :param clean: ...
        """

The line in ``bar.py`` will call ``foo()`` with ``clean="linux32"``
and ``config=None``, leading to interesting bugs.


Doc strings
^^^^^^^^^^^^

Right now the state of the docstrings inside qiBuild is quite a mess. But you
should try to write docstrings as if all of them were going to be used with
`sphinx autodoc extension <http://sphinx.pocoo.org/ext/autodoc.html>`_.

Follow `PEP257 <http://www.python.org/dev/peps/pep-0257/>`_.

So the canonical docstring should look like:

.. code-block:: python

    def foo(bar, baz):
        """Does this and that
        :param bar: ...
        :param baz: ...

        :raise: MyError if ...
        :return: True if ...
        """

But please do not put too much in the doc string, we want to keep
the code readable.

.. code-block:: python

    # Bad: too much stuff here

    def foo(bar, baz):
        """ Does this and that
        :param bar: ...
        :param baz: ...

        :raise: MyError if ...
        :return: True if ...

        .. seealso:

            * :ref:`this-other-topic`

        Example ::

          bar = Bar()
          baz = Baz()
          f = foo(bar, baz)
        """

Rather use the modularity of ``autodoc``:

.. code-block:: python

    # OK: still readable

    def foo(bar, baz):
        """ Does this and that
        :param bar: ...
        :param baz: ...

        :raise: MyError if ...
        :return: True if ...
        """


.. code-block:: rst

  .. autofunction:: qisy.sh.mkdir

  .. seealso:

    * :ref:`this-other-topic`

   Example

   .. code-block:: python

        bar = Bar()
        baz = Baz()
        f = foo(bar, baz)


Module/packages organization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Every file that ends with the python extension **must support** to be
  imported, without side effects.

* ``import foo`` must never fail, unless there is a necessary module that could
  not be found. Do not catch the ImportError unless it is necessary, for
  instance to deal with optional dependencies:

  .. code-block:: python

    import required_module

    HAS_NICE_FEATURE = True
    try:
        import nicefeature
    except ImportError:
        HAS_NICE_FEATURE = False

    #...

    if HAS_NICE_FEATURE:
        #....

* Even if you are sure you code is standalone, and is only supposed to be used
  as a script, please follow the following skeleton::

    """The foo script adds spam to the eggs """

    def add_eggs(spam, eggs):
        """Add some spam to the eggs """

        #...


    def main():
        """Parse command line """

        #...

        add_eggs(spam, eggs)

    if __name__ == "__main__":
        main()

Note that the ``main()`` function does nothing but parsing command line, the
real work being done by a nicely named ``add_eggs()`` function.

Unless you have a good reason too, please do not call ``sys.exit()`` outside of
the ``main()`` function.

You will be glad to have written your ``foo.py`` script this way if you want to
add some spam to the eggs somewhere else :)

* Keep all the imports at the beginning of the file. Separate imports from your
  package and imports from dependencies/standart library. Also separate normal
  imports and "from" imports.

  Example (bad):

  .. code-block:: python

    import foo
    from bar import toto
    import sys

    # Some code here (100 lines)

    import tata

    # Some other code here.


  Example (good):

  .. code-block:: python

    import sys

    import foo
    import tata

    from bar import toto

    # Some code here.

* If you want to shorten the name of a module, you can use ``as alias_name`` to
  rename it, but then you must keep it consistent across your whole project.

File Paths
^^^^^^^^^^

* **Never** use strings to manipulate file paths. Use built-in ``os.path``
  module which will handle all the nasty stuff for you:

  .. code-block:: python

    # BAD : you are doomed if you ever want to
    # generate a .bat file with bar_path
    bar_path = spam_path + "/" + "bar"

    # OK:
    bar_path = os.path.join(spam_path, "bar")

* When using ``os.path.join()``, use one argument per file/directory:

  .. code-block:: python

    # BAD: you can end up with an ugly path like c:\path\to/foo/bar
    my_path = os.path.join(base_dir, "foo/bar")

    # OK:
    my_path = os.path.join(base_dir, "foo", "bar")

* **Always** convert files coming from the user to native, absolute path:

  .. code-block:: python

    user_input = #...
    my_path = qibuild.sh.to_native_path(user_input)

* Always store and manipulate native paths (using ``os.path``), and if needed
  convert to POSIX or Windows format at the last moment.

  .. note::

    If you need to build POSIX paths, don't use string operations either, use
    ``posixpath.join``  (This works really well to build URL, for instance)

* Pro-tip: to hard-code paths on Windows:

  Use ``r""`` rather than ugly ``"\\"``:

  .. code-block:: python

    # UGLY:
    WIN_PATH = "c:\\windows\\spam\\eggs"

    # NICE:
    WIN_PATH = r"c:\windows\spam\eggs"


Environment Variables
^^^^^^^^^^^^^^^^^^^^^

Please make sure to **never** modify ``os.environ``

Remember that ``os.environ`` is in fact a huge global variable, and we all know
it's a bad idea to use global variables ...

Instead, use a copy of ``os.environ``, for instance:

.. code-block:: python

    import qibuild

    # Notice the .copy() !
    # If you forget it, build_env is a *reference* to
    # os.environ, so os.environ will be modified ...
    cmd_env = os.environ.copy()
    cmd_env["SPAM"] = "eggs"
    # Assuming foobar need SPAM environment variable set to 'eggs'
    cmd = ["foobar"]
    qisys.command.call(foobar, env=cmd_env)


In more complex cases, especially when handling the
``%PATH%`` environment variable, you can use ``qibuild.envsetter.EnvSetter``.

A small example:

.. code-block:: python

    import qibuild

    envsetter = qibuild.envsetter.EnvSetter()
    envsetter.prepend_to_path(r"c:\Program Files\Foobar\bin")
    build_env = envsetter.get_build_env()
    cmd = ["foobar", "/spam:eggs"]
    qisys.command.call(cmd, env=build_env)


Platform-dependent code
^^^^^^^^^^^^^^^^^^^^^^^

Please use:

.. code-block:: python

    # Windows vs everything else:
    import os
    if os.name == "posix":
        do_posix() # mac, linux
    if os.name == 'nt':
        do_windows()

    # Discriminate platform per platform:
    import sys

    if sys.platform.startswith("win"):
        # win32 or win64
        do_win()
    else if sys.platform.startswith("linux"):
        # linux, linux2 or linux3
        do_linux()
    else if sys.platform == "darwin":
        # mac
        do_mac()


Output messages to the user
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Please use ``qisys.ui`` to print nice message to the user and not just
  ``print``. This makes it easier to distinguish between real messages and the
  quick ``print`` you add for debugging.

* Speaking of debug, the tricky parts of qibuild contains some calls to
  ``qisys.ui.debug`` that are only triggered when using ``-v, --verbose``.
  Don't hesitate to use that, especially when something tricky is going on
  but you do not want to tell the user about it.


Debugging
^^^^^^^^^

When something goes wrong, you will just have the last error message printed,
with no other information. (Which is nice for the end user!)

If it's an *unexpected* error message, here is what you can do:

* run qibuild with ``-v`` flag to display debug messages

* run qibuild with ``--backtrace`` to print the full backtrace

* run qibuild with ``--pdb`` to drop to a pdb session when an uncaught exception is raised.

.. _qibuild-coding-guide-error-messages:

Error messages
^^^^^^^^^^^^^^

Please do not overlook those. Often, when writing code you do something like:

.. code-block:: python

    try:
        something_really_complicated()
    except SomeStrangeError, e:
        log.error("Error occured: %s", e)

Because you are in an hurry, and just are thinking "Great, I've handled the
exception, now I can go back to write some code..."

The problem is: the end user does not care you are glad you have handled the
exception, he needs to **understand** what happens.

So you need to take a step back, think a little. "What path would lead to
this exception? What was the end user probably doing? How can I help him
understand what went wrong, and how he can fix this?"

So here is a short list of DO's and DON'Ts when you are writing your error
messages.

* Wording should look like::

    Could not < description of what went wrong >
    <Detailed explanation>
    Please < suggestion of a solution >

  For instance::

    Could not open configuration file
    'path/to/inexistant.cfg' does not exist
    Please check your configuration.


* Put filenames between quotes. For instance, if you are using a path given
  via a GUI, or via a prompt, it's possible that you forgot to strip it before
  using it, thus trying to create ``'/path/to/foo '`` or ``'path/to/foo\n'``.

  Unless you are putting the filename between quotes, this kind of error is
  hard to notice.

* Put commands to use like this::

    Please try running: `qibuild configure -c linux32 foo'

* Give information. Code like this makes little kitten cry:

  .. code-block:: python

    try:
        with open(config_file, "w") as fp:
            config = fp.read()
    except IOError, err:
        raise Exception("Could not open config file for writing")

  It's not helpful at all! It does not answer those basic questions:

  * What was the config file?
  * What was the problem with opening the config file?
  * ...

  So the end user has **no clue** what to do... And the fix is so simple! Just
  add a few lines:

  .. code-block:: python

    try:
        with open(config_file, "w") as fp:
            config = fp.read()
    except IOError, err:
        mess = "Could not open config '%s' file for writing\n" % config_file
        mess += "Error was: %s" % err
        raise Exception(mess)

  So the error message would then be::

    Could not open '/etc/foo/bar.cfg' for writing
    Error was: [Errno 13] Permission denied

  Which is much more helpful.

* Suggest a solution. This is the hardest part, but it is nice if the user can
  figure out what to do next.

  Here are a few examples::

    $ qibuild configure -c foo

    Error: Invalid configuration foo
     * No toolchain named foo. Known toolchains are:
        ['linux32', 'linux64']
     * No custom cmake file for config foo found.
       (looked in /home/dmerejkowsky/work/tmp/qi/.qi/foo.cmake)


    $ qibuild install foo (when build dir does not exists)

    Error: Could not find build directory:
      /home/dmerejkowsky/work/tmp/qi/foo/build-linux64-release
    If you were trying to install the project, make sure that you have configured
    and built it first


    $ qibuild configure # when not in a worktree

    Error: Could not find a work tree. please try from a valid work tree,
    specify an existing work tree with '--work-tree {path}', or create a new
    work tree with 'qibuild init'


    $ qibuild configure # at the root for the worktree

    Error: Could not guess project name from the working tree. Please try
    from a subdirectory of a project or specify the name of the project.


Interacting with the user
^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure you only ask user when you have absolutely no way to do something
smart by default.

(See for instance how ``qibuild open`` ask when it has absolutely no choice
but to ask)

And when you ask, make sure the default action (pressing enter) will
do the smartest thing.

Most people will not pay attention to the questions, (and they do not
have to), so make the default obvious. (See for instance how
``qibuild config --wizard`` does it)


Adding new tests
^^^^^^^^^^^^^^^^

For historical reasons, lots of the qibuild tests still are using ``unittest``.
You should add your new test using ``py.test`` instead. Basically, for each
python module there should be a matching test module::

    qisrc/foo.py
    qisrc/test/test_foo.py

Also, when adding a new action, a good idea is to try to write the
functionality of your action thinking of it as a library, then add tests for
the library, and only then add the action.

This makes writing tests much easier, and also makes refactoring easier.

An other way to say this is that you should usually not find yourself using
`qibuild.run_action` *inside* the qibuild project, it's rather meant to be used
from a release script, for instance.

.. code-block:: python

    def continuous_tests():
        qibuild.run_action("qisrc.actions.pull")
        qibuild.run_action("qibuild.actions.configure")
        qibuild.run_action("qibuild.actions.make")
        qibuild.run_action("qibuild.actions.test")

Using external programs
^^^^^^^^^^^^^^^^^^^^^^^

To call external programs use the helpers in qisys.

And when possible use long options.

.. code-block:: sh

   # BAD
   grep -rniIEoC3 foo

   # GOOD
   grep --recursive --line-number --ignore-case --binary-files=without-match \
   --extended-regexp --only-matching --context=3 foo

It is a more readable script.
