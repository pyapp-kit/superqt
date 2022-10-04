from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs_macros.plugin import MacrosPlugin

EXAMPLES = Path(__file__).parent.parent / "examples"
IMAGES = Path(__file__).parent / "images"


def define_env(env: "MacrosPlugin"):
    @env.macro
    def insert_example(example: str, width: int = 300) -> list[Path]:
        """Grab the top widgets of the application."""
        if not example.endswith(".py"):
            example += ".py"

        src = (EXAMPLES / example).read_text()
        output = f"```python\n{src}\n```\n\n"

        dest = IMAGES / f"{example}.png"
        if not (dest).exists():
            src = src.replace("app.exec_()", "")
            exec(src)
            _grab(dest)

        output += f"![Image title](../images/{dest.name}){{ loading=lazy; width={width} }}\n\n"
        return output


def _grab(dest: str | Path) -> list[Path]:
    """Grab the top widgets of the application."""
    from qtpy.QtWidgets import QApplication

    w = next(iter(QApplication.topLevelWidgets()))
    w.grab().save(str(dest))
