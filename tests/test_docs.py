from __future__ import annotations

import importlib
import pkgutil
import re
from contextlib import suppress
from pathlib import Path
from typing import Any

import pytest

import superqt

DOCS = Path(__file__).parent.parent / "docs"
MODULES = ["superqt"] + [
    f"superqt.{m.name}"
    for m in pkgutil.iter_modules(superqt.__path__)
    if not m.name.startswith("_") and m.name != "qtcompat"  # (deprecated)
]
# objects that get an mkdocstrings section (and so an anchor, and an inventory entry)
DIRECTIVE = re.compile(r"^::: *([\w.]+)|show_members\(['\"]([\w.]+)['\"]\)", re.M)


def _resolve(path: str) -> Any:
    parts = path.split(".")
    for i in range(len(parts), 0, -1):
        with suppress(ModuleNotFoundError):
            obj = importlib.import_module(".".join(parts[:i]))
            for part in parts[i:]:
                obj = getattr(obj, part)
            return obj
    raise ImportError(path)


def _documented() -> list[Any]:
    objects = []
    for md in DOCS.rglob("*.md"):
        for path in filter(None, sum(DIRECTIVE.findall(md.read_text()), ())):
            with suppress(ImportError):  # (optional dependencies)
                objects.append(_resolve(path))
    return objects


@pytest.mark.skipif(not DOCS.exists(), reason="docs/ not available")
@pytest.mark.parametrize("module", MODULES)
def test_public_names_have_api_docs(module: str) -> None:
    mod = pytest.importorskip(module)
    documented = _documented()
    missing = [
        name
        for name in mod.__all__
        if not any(getattr(mod, name) is obj for obj in documented)
    ]
    assert not missing, f"no `:::` or `show_members` in docs/ for {module}: {missing}"

    # ... and is listed: in the widget gallery or the utilities index
    pages = ("widgets/index.md", "utilities/index.md")
    lists = "".join((DOCS / page).read_text() for page in pages)
    unlisted = [name for name in mod.__all__ if not re.search(rf"\b{name}\b", lists)]
    assert not unlisted, f"not listed in the widget or utilities index: {unlisted}"
