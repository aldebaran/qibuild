.. _qibuild-reporting:

Reporting qiBuild issues
========================


Before reporting
----------------

Preparing a detailed and well-formed bug report is not difficult, but requires
an effort on behalf of the reporter. The work done before reporting a bug is
arguably the most useful part of the job.

The following steps will guide you in preparing your bug report or feature
request.


Search for duplicates
----------------------

You should search for duplicates first.

Make sure to also browse the qibuild-dev archives, too.

https://groups.google.com/a/aldebaran-robotics.com/group/qibuild-dev/

Gather useful information
--------------------------

Here is a list of useful information that should be mentioned in your bug
report :

* Version of the package being used.
``qibuild --version`` may be useful. Also please precise where you
qibuild installation comes from.

* Add context about the system:

  * Operating system being used: Windows, Mac, Linux, 32/64bits, etc.

  * CMake generator being used: UNIX Makefiles, Visual Studio, etc.

* Add relevant information when any is available:

  * **Add the full error messages**. We make sure qibuild error messages
    are precise and useful, (see :ref:`qibuild-coding-guide-error-messages`)

  * **Add the full command line you used, and the full output**

* Indicate how to reproduce the bug. This is very important, it will help
  people test the bug and potential patches on their own computer.

* The stack trace: use ``--backtrace`` argument

For instance:

::

    Cannot frobnicate with latest qibuild

    Using qibuild from github (rev 0f452b), I get the
    following when I try to frobnicate:

    $ qibuild frobnicate --baz baz --backtrace
    Frobnicating baz
    ...

    Traceback (most recent call last):
    File "/home/dmerejkowsky/work/qi/qibuild/python/bin/qibuild", line 61, in <module>
    ...

    File "/home/dmerejkowsky/work/qi/qibuild/python/qibuild/cmake.py", line 76, in cmake
    ...

    Could not frobnicate baz:
      error was: return code is 42 instead of 41


This is a very useful bug report.

This is not:

::

    I updated qibuild and now frobnicate is broken!

Open the request
----------------

You can open the request and browse the existing issues on github:
https://github.com/aldebaran/qibuild/issues
