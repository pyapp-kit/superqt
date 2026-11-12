# CodeSyntaxHighlight

A code highlighter subclass of `QSyntaxHighlighter`
that can be used to highlight code in a QTextEdit.

Code lexer and available styles are from [`pygments`](https://pygments.org/) python library

List of available languages are available [here](https://pygments.org/languages/).

List of available styles are available [here](https://pygments.org/styles/).

## Example

{{ show_widget() }}

```python
--8<--
examples/code_syntax_highlight.py
--8<--
```

{{ show_members('superqt.utils.CodeSyntaxHighlight') }}
