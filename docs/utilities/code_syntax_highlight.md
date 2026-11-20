# CodeSyntaxHighlight

A [`QSyntaxHighlighter`](https://doc.qt.io/qt-6/qsyntaxhighlighter.html) that
highlights code in a `QTextEdit` (or any `QTextDocument`), using
[Pygments](https://pygments.org/). It takes the name of a
[language](https://pygments.org/languages/) and of a
[style](https://pygments.org/styles/), which can be changed later with
`setLanguage` and `setTheme`.

## Example

{{ show_widget() }}

```python
--8<--
examples/code_syntax_highlight.py
--8<--
```

{{ show_members('superqt.utils.CodeSyntaxHighlight') }}
