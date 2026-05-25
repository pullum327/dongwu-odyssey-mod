#!/usr/bin/env python3
"""僅套用火煉相關 Mod。"""
from __future__ import annotations

import sys

from apply_mods import main

if __name__ == "__main__":
    argv = [a for a in sys.argv[1:] if a != "--restore"]
    if "--restore" in sys.argv:
        main(["--restore"])
    else:
        main(["--only", "ignite_no_consume,ignite_changming_triple", *argv])
