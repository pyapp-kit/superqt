# Font icons

`superqt.fonticon` creates `QIcon`s from the characters (glyphs) of icon fonts,
such as [Font Awesome](https://fontawesome.com/) or
[Material Design Icons](https://pictogrammers.com/library/mdi/). Icon fonts are
installed as plugins: superqt doesn't come with any.

Compared with [`QIconifyIcon`](iconify.md), font icons don't need network
access, can be animated, and can be the text of a label or button (see the
[comparison](index.md#comparison)).

## Installing a font

These icon fonts are available as plugins, and as extras of superqt:

| Font | Install | Browse the icons |
| --- | --- | --- |
| Font Awesome 6 | `pip install "superqt[font-fa6]"` | <https://fontawesome.com/v6/search> |
| Font Awesome 5 | `pip install "superqt[font-fa5]"` | <https://fontawesome.com/v5/search> |
| Material Design Icons 7 | `pip install "superqt[font-mi7]"` | <https://pictogrammers.com/library/mdi/> |
| Material Design Icons 6 | `pip install "superqt[font-mi6]"` | <https://pictogrammers.com/library/mdi/> (shows version 7: see the [changes from version 6](https://pictogrammers.com/docs/library/mdi/releases/changelog/)) |

Other fonts are available as separate packages:

- [fonticon-bootstrapicons](https://github.com/tlambert03/fonticon-bootstrapicons)
- [fonticon-linearicons](https://github.com/tlambert03/fonticon-linearicons)
- [fonticon-feather](https://github.com/tlambert03/fonticon-feather)

[GlyphSearch](https://glyphsearch.com/) searches several icon libraries at once.
If you'd like to use a font that isn't available as a plugin, please
[open a feature request](https://github.com/pyapp-kit/superqt/issues/new/choose).

## Basic example

{{ show_widget() }}

```python
--8<--
examples/fonticon.py
--8<--
```

Glyphs are named by keys in the form `"prefix.name"`, such as `"fa5s.smile"`,
or by the constants of the classes that the plugins provide, such as
`FA5S.smile`, which IDEs autocomplete (and check for typos).

## Colors and states

`icon` takes the color, scale, opacity, and transform of the glyph. Without a
color, glyphs are black, whatever the widget's palette: for a dark theme, pass a
color (for example, one from the palette).

`states` gives other options (including another glyph) for other states and
modes of the icon. Its keys are a state (`"on"`, `"off"`), a mode (`"normal"`,
`"active"`, `"selected"`, `"disabled"`), or both (as in `"on_disabled"`). For
example, a red heart when a checkable button is checked:

```python
button.setCheckable(True)
button.setIcon(
    icon(
        FA5S.smile,
        color="gray",
        states={"on": {"glyph_key": FA5S.heart, "color": "red"}},
    )
)
```

In modes other than normal (such as disabled), a glyph without a color for that
mode is adjusted by the style, like any other icon (for example, grayed out when
disabled).

## Animations

The `animation` argument of `icon()` takes an
[`Animation`](#superqt.fonticon.Animation), such as `spin` or `pulse`, created
with the widget that shows the icon:

{{ show_widget("fonticon_animation") }}

```python
--8<--
examples/fonticon_animation.py
--8<--
```

## Glyphs as text

`setTextIcon` makes a glyph the text of a widget, such as a label or a button,
by setting its text to the glyph and its font to the icon font. The glyph is then
drawn as text, in the widget's text color, so it follows the palette and style
sheets:

```python
label = QLabel()
setTextIcon(label, FA5S.smile, size=32)
label.setStyleSheet("color: orange")
```

`font` returns the `QFont` of an icon font (by its prefix, such as `"fa5s"`), for
drawing glyphs yourself.

## Writing a plugin

Font packages register themselves with the `"superqt.fonticon"`
[entry point](https://packaging.python.org/en/latest/specifications/entry-points/)
(`superqt.fonticon.ENTRY_POINT`), and define their glyphs with an
[`IconFont`](#superqt.fonticon.IconFont) subclass (whose metaclass,
`IconFontMeta`, turns its attributes into glyph keys).
[fonticon-cookiecutter](https://github.com/tlambert03/fonticon-cookiecutter) is
a template for a new one, and the packages above are examples, such as
[fonticon-fontawesome6](https://github.com/tlambert03/fonticon-fontawesome6).
To use a font file without writing a package, see
[`addFont`](#superqt.fonticon.addFont).

## API

### Icons

::: superqt.fonticon.icon
    options:
      heading_level: 4

::: superqt.fonticon.IconOpts
    options:
      heading_level: 4

### Text

::: superqt.fonticon.setTextIcon
    options:
      heading_level: 4

::: superqt.fonticon.font
    options:
      heading_level: 4

### Fonts

::: superqt.fonticon.addFont
    options:
      heading_level: 4

::: superqt.fonticon.IconFont
    options:
      heading_level: 4

::: superqt.fonticon.IconFontMeta
    options:
      heading_level: 4

::: superqt.fonticon.ENTRY_POINT
    options:
      heading_level: 4
      show_if_no_docstring: true

### Animations

::: superqt.fonticon.Animation
    options:
      heading_level: 4

::: superqt.fonticon.spin
    options:
      heading_level: 4

::: superqt.fonticon.pulse
    options:
      heading_level: 4
