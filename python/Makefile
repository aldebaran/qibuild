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



check:
	@echo "###################################"
	@echo "running test"
	@echo "###################################"
	PYTHONPATH=. python run_tests.py

