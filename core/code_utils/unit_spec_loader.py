# -*- coding: utf-8 -*-
"""
單元 base + 題型 delta 規格組裝器。
供 sync_unit_pattern_skills.py 使用。

組合規則：
- base  = agent_skills/<unit_id>/SKILL.md
- delta = agent_skills/<unit_id>/patterns/<pattern_id>.md
- mode  = agent_skills/<unit_id>/prompt_benchmark.md 或 prompt_liveshow.md（可選）
"""

import os


def _get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def build_unit_pattern_spec(unit_id: str, pattern_id: str, mode: str = None) -> str:
    """
    組裝單元 base + 題型 delta + 可選 mode delta 的完整規格。

    Args:
        unit_id: 單元 ID（對應 agent_skills/<unit_id>/）
        pattern_id: 題型 ID（對應 patterns/<pattern_id>.md）
        mode: 可選 "benchmark" 或 "liveshow"，會合併 prompt_benchmark.md 或 prompt_liveshow.md

    Returns:
        合併後的規格字串

    Raises:
        FileNotFoundError: 當 base 或 delta 找不到時
    """
    root = _get_project_root()
    unit_dir = os.path.join(root, 'agent_skills', unit_id)

    # 1. Base
    base_path = os.path.join(unit_dir, 'SKILL.md')
    if not os.path.isfile(base_path):
        raise FileNotFoundError(f"找不到 base: {base_path}")
    with open(base_path, 'r', encoding='utf-8') as f:
        spec = f.read()

    # 2. Pattern delta
    delta_path = os.path.join(unit_dir, 'patterns', f'{pattern_id}.md')
    if not os.path.isfile(delta_path):
        raise FileNotFoundError(f"找不到 pattern delta: {delta_path}")
    with open(delta_path, 'r', encoding='utf-8') as f:
        spec += "\n\n---\n\n【題型 delta】\n\n" + f.read()

    # 3. Mode delta (optional)
    if mode and mode.lower() in ('benchmark', 'liveshow'):
        mode_path = os.path.join(unit_dir, f'prompt_{mode.lower()}.md')
        if os.path.isfile(mode_path):
            with open(mode_path, 'r', encoding='utf-8') as f:
                spec += "\n\n---\n\n【Mode delta】\n\n" + f.read()

    return spec


def list_patterns_for_unit(unit_id: str) -> list:
    """
    列出單元下所有 pattern_id（依 patterns/*.md 檔案）。

    Returns:
        [pattern_id, ...]，不含 .md 副檔名
    """
    root = _get_project_root()
    patterns_dir = os.path.join(root, 'agent_skills', unit_id, 'patterns')
    if not os.path.isdir(patterns_dir):
        return []
    out = []
    for f in os.listdir(patterns_dir):
        if f.endswith('.md'):
            out.append(f[:-3])  # strip .md
    return sorted(out)


def make_pattern_skill_id(unit_id: str, pattern_id: str) -> str:
    """
    產生 pattern skill 的 skill_id（可預測命名規則）。
    規則：<unit_id>__<pattern_id>（雙底線分隔）
    """
    return f"{unit_id}__{pattern_id}"
