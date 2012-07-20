##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010, 2012 Aldebaran Robotics
##

TEST_MODULES =
ifneq ($(MYPYMODULES),)
PYMODULES    = $(MYPYMODULES)
TEST_MODULES:= $(foreach module,$(MYPYMODULES),\
	$(shell dirname $(module))/test/test_$(shell basename $(module)).py)
TEST_MODULES:= $(foreach test,$(TEST_MODULES),\
	$(filter $(test),$(wildcard $(shell dirname $(test))/*)))
endif

PYMODULES ?= qibuild qitoolchain qisrc qixml qidoc \
	bin/qibuild                                \
	bin/qisrc                                  \
	bin/qitoolchain

PYTHON    ?= python

all: check-error check

check-all:
	@echo ":: Running pylint check-all: $(PYMODULES)"
	@pylint -f colorized --rcfile pylint.rc $(PYMODULES) --ignore=external 2>&1 || \
		exit 1 || exit 0

check-error:
	@echo ":: Running pylint --errors-only: $(PYMODULES)"
	@pylint --include-ids=y -f colorized --errors-only --rcfile pylint.rc \
		$(PYMODULES) --ignore=external 2>&1 || \
		exit 1 || exit 0
	@echo " => Checked only for pylint errors"
	@echo "    Use make check-all for running a full pylint check"

check:
	@echo ":: Running tests: $(TEST_MODULES)"
	@$(PYTHON) -m pytest $(TEST_MODULES)

check-fast:
	@echo ":: Runnig fasts tests: $(TEST_MODULES)"
	@$(PYTHON) -m pytest -k -slow $(TEST_MODULES)
