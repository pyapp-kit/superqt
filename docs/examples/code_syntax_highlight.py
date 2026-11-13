from qtpy.QtWidgets import QApplication, QTextEdit

from superqt.utils import CodeSyntaxHighlight

app = QApplication([])

text_area = QTextEdit()
# (given the QTextEdit, rather than its document, it also sets the background)
highlight = CodeSyntaxHighlight(text_area, "python", "monokai")
text_area.setPlainText(
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
text_area.resize(400, 200)
text_area.show()

app.exec()
