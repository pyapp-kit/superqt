"""Render the widget screenshots and animations used in the docs.

Each `docs/examples/<name>.py` is run offscreen, once per theme (light and dark),
and the window it shows is saved to `docs/_generated/<name>-<theme>.png`. Examples
with a scene in `docs/_scenes.py` are also recorded as `<name>-<theme>.webp`
(animated). Outputs are cached by content hash, so unchanged examples are skipped.

    uv run --group docs python docs/_gen_media.py             # everything
    uv run --group docs python docs/_gen_media.py qcollapsible --force
    uv run --group docs python docs/_gen_media.py --style macos  # native, on macOS
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from _media import main

    sys.exit(main(description=__doc__.splitlines()[0]))
