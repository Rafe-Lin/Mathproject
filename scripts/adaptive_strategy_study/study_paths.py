# -*- coding: utf-8 -*-
"""Shared repo / reports path bootstrap for adaptive_strategy_study runners."""

from __future__ import annotations

import sys
from pathlib import Path

# Directory containing this file = scripts/adaptive_strategy_study/
STUDY_ROOT = Path(__file__).resolve().parent


def repo_root() -> Path:
    """Project root (directory containing app.py)."""
    return STUDY_ROOT.parents[1]


def reports_root() -> Path:
    """Absolute path to <repo>/reports (top-level; other topics may live here)."""
    return repo_root() / "reports"


def study_reports_root() -> Path:
    """Absolute path to adaptive-strategy study outputs: <repo>/reports/adaptive_strategy_study."""
    return reports_root() / "adaptive_strategy_study"


def ensure_repo_root_on_syspath() -> Path:
    root = repo_root()
    s = str(root)
    if s not in sys.path:
        sys.path.insert(0, s)
    return root


def ensure_common_on_syspath() -> Path:
    d = STUDY_ROOT / "common"
    s = str(d)
    if s not in sys.path:
        sys.path.insert(0, s)
    return d


def ensure_exp1_effectiveness_on_syspath() -> Path:
    d = STUDY_ROOT / "exp1_effectiveness"
    s = str(d)
    if s not in sys.path:
        sys.path.insert(0, s)
    return d


def ensure_exp2_mechanism_on_syspath() -> Path:
    d = STUDY_ROOT / "exp2_mechanism"
    s = str(d)
    if s not in sys.path:
        sys.path.insert(0, s)
    return d


def ensure_exp3_reduce_c_on_syspath() -> Path:
    d = STUDY_ROOT / "exp3_reduce_c"
    s = str(d)
    if s not in sys.path:
        sys.path.insert(0, s)
    return d


def ensure_legacy_on_syspath() -> Path:
    d = STUDY_ROOT / "legacy"
    s = str(d)
    if s not in sys.path:
        sys.path.insert(0, s)
    return d


def ensure_study_root_on_syspath() -> Path:
    """So `import study_paths` works from exp* subfolders."""
    s = str(STUDY_ROOT)
    if s not in sys.path:
        sys.path.insert(0, s)
    return STUDY_ROOT
