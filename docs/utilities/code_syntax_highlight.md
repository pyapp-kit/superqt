# CodeSyntaxHighlight

A code highlighter subclass of `QSyntaxHighlighter`
that can be used to highlight code in a QTextEdit.

Code lexer and available styles are from [`pygments`](https://pygments.org/) python library

List of available languages are available [here](https://pygments.org/languages/).

List of available styles are available [here](https://pygments.org/styles/).

## Example

```python
from qtpy.QtGui import QColor, QPalette
from qtpy.QtWidgets import QApplication, QTextEdit

from superqt.utils import CodeSyntaxHighlight

app = QApplication([])

text_area = QTextEdit()

highlight = CodeSyntaxHighlight(text_area.document(), "python", "monokai")

palette = text_area.palette()
palette.setColor(QPalette.Base, QColor(highlight.background_color))
text_area.setPalette(palette)
text_area.setText(
    """from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("name", help="Your name")
    args = parser.parse_args()
    print(f"Hello {args.name}")


if __name__ == "__main__":
    main()
"""
)

text_area.show()
text_area.resize(400, 200)

app.exec_()
```

{{ show_widget() }}

{{ show_members('superqt.utils.CodeSyntaxHighlight') }}
