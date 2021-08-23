from typing import Set

from ._iconfont import IconFontMeta, namespace2font

try:
    from importlib.metadata import EntryPoint, entry_points
except ImportError:
    from importlib_metadata import EntryPoint, entry_points  # type: ignore


ENTRY_POINT = "superqt.fonticon"
_PLUGINS: dict[str, EntryPoint] = {}
_LOADED: dict[str, IconFontMeta] = {}
_BLOCKED: Set[EntryPoint] = set()


def _discover_fonts() -> None:
    _PLUGINS.clear()
    for ep in entry_points().get(ENTRY_POINT, {}):
        if ep not in _BLOCKED:
            _PLUGINS[ep.name] = ep


def _get_font_class(key: str) -> IconFontMeta:
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
    if key not in _LOADED:
        # get the entrypoint
        if key not in _PLUGINS:
            _discover_fonts()
        ep = _PLUGINS.get(key)
        if ep is None:
            raise KeyError(f"No plugin provides the key {key!r}")

        # load the entry point
        try:
            font = ep.load()
        except Exception as e:
            _PLUGINS.pop(key)
            _BLOCKED.add(ep)
            raise ImportError(f"Failed to load {ep.value}. Plugin blocked") from e

        # make sure it's a proper IconFont
        if isinstance(font, IconFontMeta):
            _LOADED[key] = font
        else:
            try:
                _LOADED[key] = namespace2font(font, ep.name.upper())
            except Exception as e:
                _PLUGINS.pop(key)
                _BLOCKED.add(ep)
                raise TypeError(
                    f"Failed to create fonticon from {ep.value}: {e}"
                ) from e
    return _LOADED[key]
