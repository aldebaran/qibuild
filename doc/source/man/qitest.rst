qitest
======

----------------------------
Working with automatic tests
----------------------------

:Manual section: 1

SYNOPSIS
--------
**qitest** command

DESCRIPTION
------------

Provides several actions to work with tests

COMMANDS
--------

run
  From a qibuild C++ projects: Run the tests declared with ``qi_create_test``

run --qitest-json QITEST_JSON
  Run the test listed in the QITEST_JSON file

run -k PATTERN
  Only run tests whose names match PATTERN
