#!/usr/bin/env python3
"""一鍵套用 mods_enabled.json 內所有已啟用 Mod（向後相容入口）。"""
from __future__ import annotations

import sys

from apply_mods import main

if __name__ == "__main__":
    main(sys.argv[1:])
