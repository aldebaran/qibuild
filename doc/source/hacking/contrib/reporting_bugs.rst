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

https://groups.google.com/a/aldebaran.com/group/qibuild-dev/

Gather useful information
--------------------------

Here is a list of useful information that should be mentioned in your bug
report :

* Version of the package being used.
  ``qibuild --version`` may be useful. Also please precise where you
  qibuild installation comes from.

* Platform used: operating system, 32/64bits, etc.

* Add relevant information when any is available:

  * **Add the full error messages**. We make sure qibuild error messages
    are precise and useful, (see :ref:`qibuild-coding-guide-error-messages`)

  * **Add the full command line you used, and the full output**

  * Make sure to run ``qibuild`` with debug output using the
    ``-v,--verbose`` option

* Indicate how to reproduce the bug. This is very important, it will help
  people test the bug and potential patches on their own computer.

* Usually qibuild crashes because of an uncaught exception. When it's the case,
  qibuild will display a bunch of text looking like::

    $ qibuild foo

    <type 'exceptions.NameError'>

    Python 2.7.11: /home/dmerejkowsky/.virtualenvs/qibuild/bin/python2
    Thu Feb 11 11:45:53 2016

    A problem occurred in a Python script.  Here is the sequence of
    function calls leading up to the error, in the order they occurred.

    ...

    /home/user/src/foo/qibuild-crash-VcC_5u/tmp_Pjifl.txt contains the description of this error.


  Please attach the .txt file in your current working directory to your bug report
  (review it for sensitive information first !)

Special case: compilation issues
++++++++++++++++++++++++++++++++

When you have a compilation issue and can't figure out what is wrong,
you will have to add even more information to your bug report.

In particular, you should:

* Run ``qibuild configure`` with ``--trace-cmake`` and attach
  the ``cmake.log`` file generated in the build directory.

* Run ``qibuild make --verbose-make -j1`` and send the full
  output of the build.

Open the request
----------------

You can open the request and browse the existing issues on github:
https://github.com/aldebaran/qibuild/issues
