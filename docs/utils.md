# Utils

## Code highlighting

`superqt` provides a code highlighter subclass of `QSyntaxHighlighter`
that can be used to highlight code in a QTextEdit.

Code lexer and available styles are from [`pygments`](https://pygments.org/) python library
List of available languages are available [here](https://pygments.org/languages/).
List of available styles are available [here](https://pygments.org/styles/).

If you would like to use this in napari widget,
then you may tant to use syntax style from napari settings.
To get current syntax style, use
`syntax_style = get_theme(get_settings().appearance.theme, as_dict=False).syntax_style`

The function `get_theme` is defined in `napari.utils.theme` module.
The function `get_settings` is defined in `napari.settings` module.
