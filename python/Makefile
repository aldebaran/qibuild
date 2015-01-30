## Copyright (c) 2009-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

TEST_MODULES =
ifneq ($(MYPYMODULES),)
PYMODULES    = $(MYPYMODULES)
TEST_MODULES:= $(foreach module,$(MYPYMODULES),\
	$(shell dirname $(module))/test/test_$(shell basename $(module)).py)
TEST_MODULES:= $(foreach test,$(TEST_MODULES),\
	$(filter $(test),$(wildcard $(shell dirname $(test))/*)))
endif


PYMODULES =  \
			qibuild         \
			qicd            \
			qidoc           \
			qilinguist      \
			qimvn           \
			qipkg           \
			qipy            \
			qisrc           \
			qisys           \
			qitest          \
			qitoolchain

PYTHON    ?= python
PIP       ?= pip

all: pylint-error check

pylint-full:
	@echo ":: Running pylint: $(PYMODULES)"
	@pylint --rcfile pylint.rc $(PYMODULES) 2>&1 || exit 1 || exit 0

pylint-error:
	@echo ":: Running pylint --errors-only: $(PYMODULES)"
	@pylint --errors-only --rcfile pylint.rc $(PYMODULES) 2>&1 || \
		exit 1 || exit 0
	@echo " => Checked only for pylint errors"
	@echo "    Use make check-all for running a full pylint check"

check:
	@echo ":: Running tests: $(TEST_MODULES)"
	@$(PYTHON) -m pytest $(PYTEST_ARGS) $(TEST_MODULES) \
				  --cov=. --cov-report=html

check-fast:
	@echo ":: Runnig fasts tests: $(TEST_MODULES)"
	@$(PYTHON) -m pytest -k -slow $(TEST_MODULES)

doc:
	@$(PYTHON) ../doc/tools/gen_cmake_doc.py ..
	@$(PYTHON) -c "from sphinx import main; main()" -b html ../doc/source ../doc/build/html

upgrade-python:
	@echo ":: Update python modules with $(PIP)"
	@$(PIP) install --user --upgrade --requirement requirements.txt
