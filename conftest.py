from unittest.mock import MagicMock
import sys

# Stub out pyxll so xl_func acts as a pass-through decorator during tests.
pyxll_mock = MagicMock()
pyxll_mock.xl_func.side_effect = lambda *args, **kwargs: (lambda fn: fn)
sys.modules["pyxll"] = pyxll_mock
