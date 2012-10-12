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

all: pylint-error check

pylint-full:
	@echo ":: Running pylint: $(PYMODULES)"
	@pylint -f colorized --rcfile pylint.rc $(PYMODULES) --ignore=external 2>&1 || \
		exit 1 || exit 0

pylint-error:
	@echo ":: Running pylint --errors-only: $(PYMODULES)"
	@pylint --include-ids=y -f colorized --errors-only --rcfile pylint.rc \
		$(PYMODULES) --ignore=external 2>&1 || \
		exit 1 || exit 0
	@echo " => Checked only for pylint errors"
	@echo "    Use make check-all for running a full pylint check"

coverage:
	@echo running tests for coverage
# cd .. is required for the Jenkins plugin to work
	@(cd .. ; $(PYTHON) -m pytest python --cov=python \
										--cov-config=coverage.ini \
										--cov-report=xml \
										--cov-report=html)
	@echo " => Open $(shell cd .. ; pwd)/htmlcov/index.html for more details"


check: pylint-error
	@echo ":: Running tests: $(TEST_MODULES)"
	@$(PYTHON) -m pytest $(TEST_MODULES)

check-fast:
	@echo ":: Runnig fasts tests: $(TEST_MODULES)"
	@$(PYTHON) -m pytest -k -slow $(TEST_MODULES)

doc:
	@$(PYTHON) ../doc/tools/gen_cmake_doc.py ..
	@$(PYTHON) -c "from sphinx import main; main()" -b html ../doc/source ../doc/build/html
