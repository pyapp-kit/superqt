# Font icons

`superqt.fonticon` creates `QIcon`s from the glyphs of icon fonts, such as
[Font Awesome](https://fontawesome.com/) or
[Material Design Icons](https://pictogrammers.com/library/mdi/). Unlike images,
glyphs can be drawn at any size and in any color.

Icon fonts are installed as plugins (see [below](#font-icon-plugins)), and glyphs
are referred to by a key in the form `"prefix.name"`, such as `"fa5s.smile"`. The
plugins also provide classes with a constant for each glyph, such as
`FA5S.smile`, which IDEs can autocomplete.

## Basic example

{{ show_widget() }}

```python
--8<--
examples/fonticon.py
--8<--
```

`icon` takes options for the color, scale, and animation of the glyph, and
different options for each state and mode of the icon (as in
`QIcon.State` and `QIcon.Mode`); see [`icon`](#superqt.fonticon.icon) below.

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

## Font icon plugins

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

### Writing a plugin

Font packages register themselves with the `"superqt.fonticon"`
[entry point](https://packaging.python.org/en/latest/specifications/entry-points/).
[fonticon-cookiecutter](https://github.com/tlambert03/fonticon-cookiecutter) is
a template for a new one, and the packages above are examples, such as
[fonticon-fontawesome6](https://github.com/tlambert03/fonticon-fontawesome6).
To use a font file without writing a package, see
[`addFont`](#superqt.fonticon.addFont).

## API

::: superqt.fonticon.icon
    options:
      heading_level: 3

::: superqt.fonticon.setTextIcon
    options:
      heading_level: 3

::: superqt.fonticon.font
    options:
      heading_level: 3

::: superqt.fonticon.IconOpts
    options:
      heading_level: 3

::: superqt.fonticon.addFont
    options:
      heading_level: 3

::: superqt.fonticon.IconFont
    options:
      heading_level: 3

::: superqt.fonticon.Animation
    options:
      heading_level: 3

::: superqt.fonticon.pulse
    options:
      heading_level: 3

::: superqt.fonticon.spin
    options:
      heading_level: 3
