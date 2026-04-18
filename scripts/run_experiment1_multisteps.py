# -*- coding: utf-8 -*-
"""Compatibility shim: forwards to adaptive_strategy_study Exp1 runner."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent
    / "adaptive_strategy_study"
    / "exp1_effectiveness"
    / "run_experiment1_multisteps.py"
)

if __name__ == "__main__":
    sys.argv[0] = str(_TARGET)
    runpy.run_path(str(_TARGET), run_name="__main__")
