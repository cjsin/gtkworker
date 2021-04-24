PACKAGE_NAME := gtkworker
ACTIVATE     := . venv/bin/activate
VERSION      := $(shell tr -d ' ' < setup.cfg | awk -F= '/^version=/ {print $$2}')
DISTWHEEL    := dist/$(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl

version:
	@echo Package: $(PACKAGE_NAME)
	@echo Version: $(VERSION)
	@echo Wheel: $(DISTWHEEL)

example:
	PYTHONPATH=$(PWD)/src python3 -m gtkworker.example

example2:
	PYTHONPATH=$(PWD)/src python3 -m gtkworker.example2

lint:
	pylint-3 src

build-reqs:
	pip list | egrep '^build[[:space:]]' || python3 -m pip install --upgrade build

build: build-reqs
	python3 -m build

$(DISTHWEEL): build

clean-venv:
	rm -rf ./venv

venv:
	python3 -m venv venv

venv-install: venv $(DISTWHEEL)
	$(ACTIVATE) && pip install $(DISTWHEEL)

venv-run-example2: venv-install
	$(ACTIVATE) && python3 -m gtkworker.example2

venv-run-example: venv-install
	$(ACTIVATE) python3 -m gtkworker.example

venv-test: clean-venv venv-run-example2 venv-run-example
