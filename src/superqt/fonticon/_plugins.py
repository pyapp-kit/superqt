import contextlib
from typing import ClassVar

from ._iconfont import IconFontMeta, namespace2font

try:
    from importlib.metadata import EntryPoint, entry_points
except ImportError:
    from importlib_metadata import EntryPoint, entry_points  # type: ignore


class FontIconManager:
    ENTRY_POINT: ClassVar[str] = "superqt.fonticon"
    _PLUGINS: ClassVar[dict[str, EntryPoint]] = {}
    _LOADED: ClassVar[dict[str, IconFontMeta]] = {}
    _BLOCKED: ClassVar[set[EntryPoint]] = set()

    def _discover_fonts(self) -> None:
        self._PLUGINS.clear()
        entries = entry_points()
        if hasattr(entries, "select"):  # python>3.10
            _entries = entries.select(group=self.ENTRY_POINT)  # type: ignore
        else:
            _entries = entries.get(self.ENTRY_POINT, [])
        for ep in _entries:
            if ep not in self._BLOCKED:
                self._PLUGINS[ep.name] = ep

    def _get_font_class(self, key: str) -> IconFontMeta:
        """Get IconFont given a key.

        Parameters
        ----------
        key : str
            font key to load.

        Returns
        -------
        IconFontMeta
            Instance of IconFontMeta

        Raises
        ------
        KeyError
            If no plugin provides this key
        ImportError
            If a plugin provides the key, but the entry point doesn't load
        TypeError
            If the entry point loads, but is not an IconFontMeta
        """
        if key not in self._LOADED:
            # get the entrypoint
            if key not in self._PLUGINS:
                self._discover_fonts()
            ep = self._PLUGINS.get(key)
            if ep is None:
                raise KeyError(f"No plugin provides the key {key!r}")

            # load the entry point
            try:
                font = ep.load()
            except Exception as e:
                self._PLUGINS.pop(key)
                self._BLOCKED.add(ep)
                raise ImportError(f"Failed to load {ep.value}. Plugin blocked") from e

            # make sure it's a proper IconFont
            try:
                self._LOADED[key] = namespace2font(font, ep.name.upper())
            except Exception as e:
                self._PLUGINS.pop(key)
                self._BLOCKED.add(ep)
                raise TypeError(
                    f"Failed to create fonticon from {ep.value}: {e}"
                ) from e
        return self._LOADED[key]

    def dict(self) -> dict:
        return {
            key: sorted(filter(lambda x: not x.startswith("_"), cls.__dict__))
            for key, cls in self._LOADED.items()
        }


_manager = FontIconManager()
get_font_class = _manager._get_font_class


def discover() -> tuple[str]:
    _manager._discover_fonts()


def available() -> tuple[str]:
    return tuple(_manager._PLUGINS)


def loaded(load_all=False) -> dict[str, list[str]]:
    if load_all:
        discover()
        for x in available():
            with contextlib.suppress(Exception):
                _manager._get_font_class(x)
    return {
        key: sorted(filter(lambda x: not x.startswith("_"), cls.__dict__))
        for key, cls in _manager._LOADED.items()
    }
