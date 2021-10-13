PACKAGE_NAME = gtkworker

include Makefile.pymodule

OPTIONALS    = attrdict

RUN_MAIN     = $(RUN_PY_MOD) $(PACKAGE_NAME)
RUN_EXAMPLE1 = $(RUN_PY_MOD) $(PACKAGE_NAME).example1
RUN_EXAMPLE2 = $(RUN_PY_MOD) $(PACKAGE_NAME).example2
RUN_EXAMPLES = ( $(RUN_EXAMPLE1 && $(RUN_EXAMPLE2) )


venv-run-example1: venv-install
	$(WITH_VENV) $(RUN_EXAMPLE1)

venv-run-example2: venv-install
	$(WITH_VENV) $(RUN_EXAMPLE2)

venv-run-examples: venv-run-example1 venv-run-example2

venv-run-tests: venv-install
	$(WITH_VENV) $(RUN_TESTS)

venv-test: clean-venv venv-run-examples venv-run-tests

examples: example1 example2

example1:
	$(WITH_PYPATH) $(RUN_EXAMPLE1)

example2:
	$(WITH_PYPATH) $(RUN_EXAMPLE2)

test: venv
	$(WITH_VENV) $(RUN_TESTS)

run: examples

test-targets1: clean-docs clean-venv clean
test-targets2: docs clean-docs clean
test-targets3: build wheel venv-install clean
test-targets4: venv-run-tests venv-run-examples clean
test-targets5: test examples clean

test-makefile-targets:
	for n in $$(seq 1 5) ; do make test-targets$$n || exit 1; done
	echo all targets completed successfully
