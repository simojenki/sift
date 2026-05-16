import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_loader = SourceFileLoader("sift", str(Path(__file__).parent.parent / "src" / "sift"))
_spec = importlib.util.spec_from_loader("sift", _loader)
_module = importlib.util.module_from_spec(_spec)
_loader.exec_module(_module)
sys.modules["sift"] = _module
