import sys
from enum import EnumMeta
from importlib import import_module
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

from jinja2 import pass_context
from qtpy.QtCore import QObject, Signal

if TYPE_CHECKING:
    from mkdocs_macros.plugin import MacrosPlugin

EXAMPLES = Path(__file__).parent.parent / "examples"
IMAGES = Path(__file__).parent / "_auto_images"
IMAGES.mkdir(exist_ok=True, parents=True)


def define_env(env: "MacrosPlugin"):
    @env.macro
    @pass_context
    def show_widget(context, width: int = 500) -> list[Path]:
        # extract all fenced code blocks starting with "python"
        page = context["page"]
        dest = IMAGES / f"{page.title}.png"
        if "build" in sys.argv:
            dest.unlink(missing_ok=True)

            codeblocks = [
                b[6:].strip()
                for b in page.markdown.split("```")
                if b.startswith("python")
            ]
            src = codeblocks[0].strip()
            src = src.replace(
                "QApplication([])", "QApplication.instance() or QApplication([])"
            )
            src = src.replace("app.exec_()", "app.processEvents()")

            exec(src)
            _grab(dest, width)
        return (
            f"![{page.title}](../{dest.parent.name}/{dest.name})"
            f"{{ loading=lazy; width={width} }}\n\n"
        )

    @env.macro
    def show_members(cls: str):
        # import class
        module, name = cls.rsplit(".", 1)
        _cls = getattr(import_module(module), name)

        first_q = next(
            (
                b.__name__
                for b in _cls.__mro__
                if issubclass(b, QObject) and ".Qt" in b.__module__
            ),
            None,
        )

        inherited_members = set()
        for base in _cls.__mro__:
            if issubclass(base, QObject) and ".Qt" in base.__module__:
                inherited_members.update(
                    {k for k in dir(base) if not k.startswith("_")}
                )

        new_signals = {
            k
            for k, v in vars(_cls).items()
            if not k.startswith("_") and isinstance(v, Signal)
        }

        self_members = {
            k
            for k in dir(_cls)
            if not k.startswith("_") and k not in inherited_members | new_signals
        }

        enums = []
        for m in list(self_members):
            if isinstance(getattr(_cls, m), EnumMeta):
                self_members.remove(m)
                enums.append(m)

        out = ""
        if first_q:
            url = f"https://doc.qt.io/qt-6/{first_q.lower()}.html"
            out += f"## Qt Class\n\n<a href='{url}'>`{first_q}`</a>\n\n"

        out += ""

        if new_signals:
            out += "## Signals\n\n"
            for sig in new_signals:
                out += f"### `{sig}`\n\n"

        if enums:
            out += "## Enums\n\n"
            for e in enums:
                out += f"### `{_cls.__name__}.{e}`\n\n"
                for m in getattr(_cls, e):
                    out += f"- `{m.name}`\n\n"

        if self_members:
            out += dedent(
                f"""
            ## Methods

            ::: {cls}
                options:
                  heading_level: 3
                  show_source: False
                  show_inherited_members: false
                  show_signature_annotations: True
                  members: {sorted(self_members)}
                  docstring_style: numpy
                  show_bases: False
                  show_root_toc_entry: False
                  show_root_heading: False
            """
            )

        return out


def _grab(dest: str | Path, width) -> list[Path]:
    """Grab the top widgets of the application."""
    from qtpy.QtWidgets import QApplication

    w = QApplication.topLevelWidgets()[-1]
    w.setFixedWidth(width)
    w.activateWindow()
    w.setMinimumHeight(40)
    w.grab().save(str(dest))
