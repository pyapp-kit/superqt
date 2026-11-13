"""Macros for the superqt docs (see `[project.plugins.macros]` in zensical.toml)."""

from __future__ import annotations

import ast
import inspect
import json
import os
import sys
from enum import EnumMeta
from importlib import import_module
from pathlib import Path
from textwrap import dedent, indent
from typing import TYPE_CHECKING, Any

from qtpy.QtCore import Property, QObject, Signal

if TYPE_CHECKING:
    from collections.abc import Iterator

DOCS = Path(__file__).parent
MANIFEST = DOCS / "_generated" / "manifest.json"
QT_DOCS = "https://doc.qt.io/qt-6/{}.html"


def define_env(env: Any) -> None:
    @env.macro
    def show_widget(name: str | None = None) -> str:
        """Theme-aware screenshot (or animation) of `docs/examples/<name>.py`.

        `name` defaults to the name of the page.
        """
        page = env.variables["page"]
        name = name or Path(page.path).stem
        info = _manifest().get(name)
        if info is None:
            msg = _missing(name)
            return f'!!! warning "Missing screenshot"\n\n    {msg}\n'

        root = "../" * Path(page.path).as_posix().count("/") + "_generated/"
        animated = "animation" in info
        ext, size = ("webp", info["animation"]) if animated else ("png", info)
        attrs = f'width="{size["width"]}" height="{size["height"]}" loading=lazy'
        imgs = "\n".join(
            f"![{page.title}]({root}{name}-{theme}.{ext}#only-{theme}){{ {attrs} }}"
            for theme in ("light", "dark")
        )
        return f'<figure class="sq-demo" markdown="span">\n{imgs}\n</figure>\n'

    @env.macro
    def card(page_ref: str, title: str, description: str) -> str:
        """Gallery card linking to `page_ref`, with its widget's screenshot."""
        page = env.variables["page"]
        name = Path(page_ref).stem
        thumb = style = ""
        if (info := _manifest().get(name)) is None:
            _missing(name)
        else:
            root = "../" * Path(page.path).as_posix().count("/") + "_generated/"
            # the still, and the animation (if any), which plays on hover
            images = [("png", info, ".sq-card__still" if "animation" in info else "")]
            if anim := info.get("animation"):
                images.append(("webp", anim, ".sq-card__anim"))
            thumb = "".join(
                f"![]({root}{name}-{theme}.{ext}#only-{theme})"
                f'{{ {cls} width="{size["width"]}" loading=lazy }}'
                for ext, size, cls in images
                for theme in ("light", "dark")
            )
            # match the window color of the screenshots
            bg = info.get("background", {})
            style = "".join(f"--sq-thumb-{t}: {c}; " for t, c in bg.items())
        return (
            f'[<span class="sq-card__thumb" style="{style.strip()}">{thumb}</span>'
            f'<span class="sq-card__body"><strong>{title}</strong>'
            f"<span>{description}</span></span>]({page_ref}){{ .sq-card }}"
        )

    @env.macro
    def show_members(cls_path: str) -> str:
        """API of a widget: its class, Qt base class, signals, enums, and methods.

        The class's heading (anchored, and in `objects.inv`) heads the section.
        """
        module, name = cls_path.rsplit(".", 1)
        cls = getattr(import_module(module), name)
        qt_base = next((b for b in cls.__mro__ if _is_qt(b)), None)
        qt_members = {m for b in cls.__mro__ if _is_qt(b) for m in dir(b)}
        signals = dict(_signals(cls))

        out = [_mkdocstrings_class(cls_path)]
        if qt_base is not None:
            link = f"[`{qt_base.__name__}`]({QT_DOCS.format(qt_base.__name__.lower())})"
            out.append(
                f'!!! abstract "Subclass of {qt_base.__name__}"\n\n'
                f"    `{cls.__name__}` inherits all of {link}'s methods, signals, and "
                "properties. Only those that `superqt` adds or changes are listed "
                "here.\n"
            )

        if signals:
            out.append("### Signals\n")
            for sig, (args, doc) in signals.items():
                out.append(f"- `{sig}({args})`" + (f": {doc}" if doc else ""))
            out.append("")

        public = {m for m in dir(cls) if not m.startswith("_")}
        enums = sorted(
            m for m in public - qt_members if isinstance(getattr(cls, m), EnumMeta)
        )
        if enums:
            out.append("### Enums\n")
            for enum_name in enums:
                values = ", ".join(f"`{m.name}`" for m in getattr(cls, enum_name))
                out.append(f"`{cls.__name__}.{enum_name}`\n:   {values}\n")

        names = (public - qt_members) | _documented_overrides(cls, public & qt_members)
        names -= set(signals) | set(enums) | {n for n in names if n.isupper()}
        props = sorted(n for n in names if isinstance(getattr(cls, n), Property))
        methods = sorted(names - set(props))
        for title, members in (("Properties", props), ("Methods", methods)):
            if members:
                out.append(f"### {title}\n\n{_mkdocstrings(cls_path, members)}")
        return "\n".join(out)


def _mkdocstrings_class(cls_path: str) -> str:
    """The class's heading (level 2), signature, and docstring, without members."""
    options = """
    options:
      heading_level: 2
      show_root_heading: true
      show_root_toc_entry: true
      members: false
      overloads_only: true
    """
    return f"::: {cls_path}\n{indent(dedent(options), '    ')}\n"


def _mkdocstrings(cls_path: str, members: list[str]) -> str:
    options = f"""
    options:
      heading_level: 4
      show_root_heading: false
      show_root_toc_entry: false
      show_docstring_description: true
      inherited_members: true
      show_if_no_docstring: true
      members: {members}
    """
    return f"::: {cls_path}\n{indent(dedent(options), '    ')}"


# Qt virtuals that superqt reimplements as implementation details
_VIRTUALS = {"event", "eventFilter", "initStyleOption", "sizeHint", "minimumSizeHint"}
_VIRTUALS |= {"checkStateSet", "nextCheckState", "setStyleSheet"}


def _documented_overrides(cls: type, names: set[str]) -> set[str]:
    """Qt methods that superqt reimplements and documents (e.g. `value()`)."""
    out = set()
    for name in names - _VIRTUALS:
        if name.endswith("Event"):
            continue
        owner = next(b for b in cls.__mro__ if name in vars(b))
        if owner.__module__.startswith("superqt") and inspect.getdoc(vars(owner)[name]):
            out.add(name)
    return out


def _missing(name: str) -> str:
    """Raise in CI, else warn (so that `zensical serve` keeps running)."""
    msg = f"No screenshot of `{name}` yet: run `docs/_gen_media.py`."
    if os.environ.get("CI"):  # (`--strict` ignores the warnings of macros)
        raise RuntimeError(msg)
    print(f"warning: {msg}", file=sys.stderr)
    return msg


def _manifest() -> dict[str, dict]:  # (not cached: `zensical serve` may run long)
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}


def _is_qt(cls: type) -> bool:
    return issubclass(cls, QObject) and ".Qt" in cls.__module__


def _signals(cls: type) -> Iterator[tuple[str, tuple[str, str]]]:
    """Signals declared on `cls` or its superqt bases: name -> (arguments, doc).

    The doc is a string literal after the signal (an attribute docstring), or the
    comment above it, or a trailing `# emitted when...` comment.
    """
    seen: set[str] = set()
    for base in cls.__mro__:
        if not base.__module__.startswith("superqt"):
            continue
        lines, _ = inspect.getsourcelines(base)
        body = ast.parse(dedent("".join(lines))).body[0].body  # type: ignore
        for node, after in zip(body, [*body[1:], None], strict=True):
            if not (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Name)
                and isinstance(getattr(base, node.targets[0].id, None), Signal)
            ):
                continue
            sig = node.targets[0].id
            if sig.startswith("_") or sig in seen:
                continue
            seen.add(sig)
            call = node.value
            args = ", ".join(ast.unparse(a) for a in getattr(call, "args", []))
            if (
                isinstance(after, ast.Expr)
                and isinstance(after.value, ast.Constant)
                and isinstance(after.value.value, str)
            ):
                doc = " ".join(after.value.value.split())
            elif above := _comment_above(lines, node.lineno - 1):
                doc = above
            else:
                comment = lines[node.lineno - 1].partition("#")[2].strip()
                doc = comment.capitalize() if comment.startswith("emitted") else ""
            yield sig, (args, doc)


def _comment_above(lines: list[str], index: int) -> str:
    comments: list[str] = []
    while index > 0 and (line := lines[index - 1].strip()).startswith("#"):
        comments.insert(0, line.lstrip("# "))
        index -= 1
    text = ""
    for comment in comments:  # (join sentences that were split across lines)
        if text and text[-1] not in ".,;:" and comment[:1].isupper():
            text += "."
        text = f"{text} {comment}" if text else comment
    return text
