---
hide:
  - toc
---

# Icons

superqt can create a `QIcon` from an icon library in two ways:

- [`QIconifyIcon`](iconify.md) uses the SVG icons of [Iconify](https://iconify.design/):
  over 450,000 icons, from more than 260 icon sets (including Bootstrap Icons,
  Font Awesome, and Material Design Icons). It's the usual choice: any icon is
  available without choosing an icon set in advance.
- [Font icons](fonticon.md) (`superqt.fonticon`) draw the characters of icon
  fonts that you install as plugins. They work without network access, can be
  animated, and can be the text of a label or button.

<div class="sq-gallery sq-gallery--center" markdown>
{{ card("iconify.md", "QIconifyIcon", "Any of Iconify's SVG icons, downloaded when first used.") }}
{{ card("fonticon.md", "Font icons", "Glyphs of installed icon fonts, drawn as text.") }}
</div>

## Comparison

Most of the differences follow from one detail: `QIconifyIcon` draws SVG images
that are downloaded (and cached) the first time they're used, while
`superqt.fonticon` draws the characters of a font file that's installed in
advance, as a plugin.

| | [`QIconifyIcon`](iconify.md) | [`superqt.fonticon`](fonticon.md) |
| --- | --- | --- |
| **What it draws** | An SVG image, drawn by Qt's SVG support | A character of an icon font, drawn as text |
| In text | No: only where an icon or image goes | Yes: [`setTextIcon`](fonticon.md#glyphs-as-text) makes a glyph the text of a label or button (in its text color), and `font()` gives the font |
| Colors | One color with `color=`, or the icon's own colors (e.g. emoji) | One color: the glyph's |
| Animation | No | `spin`, `pulse`, or a custom `Animation` |
| **Icons available** | Over 450,000 icons, from 260+ icon sets | Only fonts installed as plugins (none by default): Font Awesome 5 and 6, Material Design Icons 6 and 7, and a few others |
| Install | `superqt[iconify]` (pyconify, requests) | One package per font (e.g. `superqt[font-fa6]`), which contains the font |
| Network | Each icon is [downloaded on first use](iconify.md#how-icons-are-fetched), then cached on disk; offline and uncached, you get a "?" placeholder | None |
| **Naming icons** | `"prefix:name"` strings | Constants with IDE autocompletion and typo checking, such as `FA5S.smile`, or `"fa5s.smile"` strings |
| Per state/mode | `addKey(..., mode=, state=)` | `states={...}` |
| Bundling with an app | [Ship a pre-filled pyconify cache](iconify.md#using-icons-offline-or-in-an-app) | The font is in the plugin package |
