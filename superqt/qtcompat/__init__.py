from __future__ import annotations

import os
import sys
import warnings
from importlib import abc, import_module, util
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from types import ModuleType


class QtMissingError(ImportError):
    """Error raise if no bindings could be selected."""


VALID_APIS = {
    "pyqt5": "PyQt5",
    "pyqt6": "PyQt6",
    "pyside2": "PySide2",
    "pyside6": "PySide6",
}

# Detecting if a binding was specified by the user
_requested_api = os.getenv("QT_API", "").lower()
_forced_api = os.getenv("FORCE_QT_API")

if _requested_api and _requested_api not in VALID_APIS:
    warnings.warn(
        f"invalid QT_API specified: {_requested_api}. "
        f"Valid values include {set(VALID_APIS)}"
    )
    _forced_api = None
    _requested_api = ""

# TODO: FORCE_QT_API requires also using QT_API ... does that make sense?


_QtCore: ModuleType | None = None
if not _forced_api:
    # If `FORCE_QT_API` is not set, we first look for previously imported bindings
    for api_name, module_name in VALID_APIS.items():
        if module_name in sys.modules:
            _QtCore = import_module(f"{module_name}.QtCore")
            break

if _QtCore is None:
    requested = VALID_APIS.get(_requested_api)
    mod_names = sorted(VALID_APIS.values(), key=lambda x: x != requested)
    for module_name in mod_names:
        try:
            _QtCore = import_module(f"{module_name}.QtCore")
            break
        except ImportError:
            if _forced_api:
                ImportError(
                    "FORCE_QT_API set and unable to import requested QT_API: {e}"
                )

if _QtCore is None:
    raise QtMissingError(f"No QtCore could be found. Tried: {VALID_APIS.values()}")

QT_VERSION = getattr(_QtCore, "QT_VERSION_STR", None) or getattr(_QtCore, "__version__")
API_NAME = _QtCore.__name__.split(".", maxsplit=1)[0]
PYSIDE2 = API_NAME == "PySide2"
PYSIDE6 = API_NAME == "PySide6"
PYQT5 = API_NAME == "PyQt5"
PYQT6 = API_NAME == "PyQt6"

if _requested_api and API_NAME != VALID_APIS[_requested_api]:
    warnings.warn(
        f"Selected binding {_requested_api!r} could not be found, using {API_NAME!r}"
    )


class SuperQtImporter(abc.MetaPathFinder):
    def find_spec(
        self,
        fullname: str,
        path: Sequence[bytes | str] | None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        """Find a spec for the specified module.

        See https://docs.python.org/3/reference/import.html#the-meta-path
        """
        if fullname.startswith(__name__):
            return util.find_spec(fullname.replace(__name__, API_NAME))
        return None


def _get_submodule(mod_name: str):
    _mod = mod_name.rsplit(".", maxsplit=1)[-1]
    return import_module(f"{API_NAME}.{_mod}")


sys.meta_path.append(SuperQtImporter())
