## Copyright (c) 2009-2018 SoftBank Robotics. All rights reserved.
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

all: pycodestyle pylint check

pycodestyle:
	@echo :: Running pycodestyle on root folder
	@pycodestyle .. 2>&1

pylint:
	@echo :: Running pylint: $(PYMODULES)
	@pylint $(PYMODULES) 2>&1

check:
	@echo :: Running tests:
	@$(PYTHON) -m pytest $(PYTEST_ARGS) $(TEST_MODULES) --cov=. --cov-report=html -n auto

doc:
	qidoc build qibuild
