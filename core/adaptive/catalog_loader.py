# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
from pathlib import Path

from .schema import CatalogEntry


DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "自適應實作" / "skill_breakpoint_catalog.csv"


def _read_rows(path: Path) -> list[dict[str, str]]:
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp950"):
        try:
            with path.open("r", encoding=encoding, newline="") as fh:
                reader = csv.DictReader(fh)
                return [dict(row) for row in reader]
        except Exception as exc:  # pragma: no cover
            last_error = exc
    raise RuntimeError(f"Failed to read catalog {path}: {last_error}")


def load_catalog(path: str | Path | None = None) -> list[CatalogEntry]:
    catalog_path = Path(path) if path else DEFAULT_CATALOG_PATH
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")

    rows = _read_rows(catalog_path)
    return [CatalogEntry.from_row(row) for row in rows]


def build_family_index(path: str | Path | None = None) -> dict[str, CatalogEntry]:
    entries = load_catalog(path)
    return {f"{entry.skill_id}:{entry.family_id}": entry for entry in entries}
