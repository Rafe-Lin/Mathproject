# -*- coding: utf-8 -*-
"""Compatibility shim: forwards to adaptive_strategy_study Exp2 engine."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parent
    / "adaptive_strategy_study"
    / "exp2_mechanism"
    / "simulate_student.py"
)

if __name__ == "__main__":
    sys.argv[0] = str(_TARGET)
    runpy.run_path(str(_TARGET), run_name="__main__")
