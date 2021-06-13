"""
Tests for gtkworker class.
Unfortunately testing the gtk side would require a display and
wouldn't run in CI, so this does little more than import the module.
"""

# pylint: disable=missing-function-docstring

def test_imports():
    # pylint: disable=unused-import,import-outside-toplevel
    import gtkworker
