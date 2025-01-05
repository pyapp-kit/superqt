# QIconifyIcon

[Iconify](https://iconify.design/) is an icon library that includes 150,000+
icons from most major icon sets including Bootstrap, FontAwesome, Material
Design, and many more; each available as individual SVGs.  Unlike the
[`superqt.fonticon` module](./fonticon.md), `superqt.QIconifyIcon` does not require any additional
dependencies or font files to be installed.  Icons are downloaded (and cached)
on-demand from the Iconify API, using [pyconify](https://github.com/pyapp-kit/pyconify)

Search availble icons at <https://icon-sets.iconify.design>
Once you find one you like, use the key in the format `"prefix:name"` to create an
icon:  `QIconifyIcon("bi:bell")`.

## Basic Example

```python
from qtpy.QtCore import QSize
from qtpy.QtWidgets import QApplication, QPushButton

from superqt import QIconifyIcon

app = QApplication([])

btn = QPushButton()
btn.setIcon(QIconifyIcon("fluent-emoji-flat:alarm-clock"))
btn.setIconSize(QSize(60, 60))
btn.show()

app.exec()
```

{{ show_widget(225) }}

::: superqt.QIconifyIcon
    options:
        heading_level: 3
