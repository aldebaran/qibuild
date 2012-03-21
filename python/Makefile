##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

PYMODULES=qibuild qitoolchain qisrc \
          bin/qibuild               \
          bin/qisrc                 \
          bin/qitoolchain

PYTHON ?= python

all: check-error check

check-all:
	@echo ":: Running pylint check-all"
	@pylint -f colorized --rcfile pylint.rc $(PYMODULES) --ignore=external 2>&1 | grep -v "Exception RuntimeError: 'maximum recursion depth exceeded" && exit 1 || exit 0

check-error:
	@echo ":: Running pylint --errors-only"
	@pylint --include-ids=y -f colorized --errors-only --rcfile pylint.rc $(PYMODULES) --ignore=external 2>&1 | grep -v "Exception RuntimeError: 'maximum recursion depth exceeded" && exit 1 || exit 0
	@echo " => Checked only for pylint errors"
	@echo "    Use make check-all for running a full pylint check"

check:
	@echo ":: Running tests"
	@$(PYTHON) run_tests.py


coverage:
	@echo ":: Running tests (with coverage)"
	@rm -fr .coverage htmlcov
	@$(PYTHON) run_tests.py --coverage
	@$(PYTHON) -m coverage html


# To be run on a build farm:
continuous: check-error
	@$(PYTHON) run_tests.py --coverage --xunit

