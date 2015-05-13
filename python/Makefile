## Copyright (c) 2009-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

PYMODULES =  \
			qibuild         \
			qicd            \
			qidoc           \
			qilinguist      \
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
	@echo ":: Running tests:"
	@$(PYTHON) -m pytest $(PYTEST_ARGS) $(TEST_MODULES) \
				  --cov=. --cov-report=html \
				  -n `nproc`

doc:
	qidoc build qibuild
