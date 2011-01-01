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

all: check-error check
	@echo ""
	@echo "###################################"
	@echo "GG, now you can commit!"
	@echo "###################################"

check-all:
	@echo "###################################"
	@echo "running pylint check-all"
	@echo "###################################"
	@pylint -f colorized --rcfile pylint.rc $(PYMODULES) --ignore=gui 2>&1 | grep -v "Exception RuntimeError: 'maximum recursion depth exceeded" && exit 1 || exit 0

check-error:
	@echo "###################################"
	@echo "# running pylint check-error"
	@echo "###################################"
	@pylint --include-ids=y -f colorized --errors-only --rcfile pylint.rc $(PYMODULES) --ignore=gui 2>&1 | grep -v "Exception RuntimeError: 'maximum recursion depth exceeded" && exit 1 || exit 0
	@echo " >checked only for pylint error (use check-all for more)"

check-release:
	@echo "###################################"
	@echo "# Checking that everything is OK for a release"
	@echo "###################################"
	@python bin/dorelease quickcheck
	pylint --rcfile pylint.rc --errors-only actions/release 2>&1 | grep -v "Exception RuntimeError: 'maximum recursion depth exceeded" && exit 1 || exit 0



pep8:
	@echo "###################################"
	@echo "checking code conform to pep8"
	@python pep8.py --filename="*.py" .
	@echo ""


check: test/conf.py
	@echo "###################################"
	@echo "running test"
	@echo "###################################"
	PYTHONPATH=. python test/test.py

check-debug: test/conf.py
	@echo "###################################"
	@echo "to run test with pdb launch:"
	@echo "PYTHONPATH=. python test/test.py -d"
	@echo "###################################"


test/conf.py: test/conf.py.in
	@echo "###################################"
	@echo "Generating a sample test/conf.py"
	@echo "Please edit this file to meet your settings"
	@echo "###################################"
	cp test/conf.py.in test/conf.py
