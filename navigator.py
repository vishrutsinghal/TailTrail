#!/usr/bin/env python3
"""Repository-root compatibility entry point for the canonical Navigator."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent / "scripts"
if SCRIPTS.as_posix() not in sys.path:
    sys.path.insert(0, SCRIPTS.as_posix())

from scripts.navigator import decide, main  # noqa: E402,F401


if __name__ == "__main__":
    raise SystemExit(main())
