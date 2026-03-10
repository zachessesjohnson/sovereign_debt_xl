from unittest.mock import MagicMock
import sys

# Stub out pyxll so xl_func acts as a pass-through decorator during tests.
pyxll_mock = MagicMock()
pyxll_mock.xl_func.side_effect = lambda *args, **kwargs: (lambda fn: fn)
# xl_image: return the raw bytes from the BytesIO so tests can inspect PNG output.
pyxll_mock.xl_image.side_effect = lambda data=None, **kw: (data.read() if hasattr(data, "read") else data)
sys.modules["pyxll"] = pyxll_mock

