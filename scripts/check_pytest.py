import sys

try:
    import pytest
    print("PYTEST_OK", pytest.__version__)
except Exception as e:
    print("PYTEST_MISSING", e)
    sys.exit(2)

