from qtpy.QtWidgets import QApplication, QTextEdit

from superqt.utils import CodeSyntaxHighlight

app = QApplication([])

text_area = QTextEdit()

highlight = CodeSyntaxHighlight(text_area.document(), "python", "default")

text_area.setText(
    """
from argparse import ArgumentParser

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

app.exec_()
