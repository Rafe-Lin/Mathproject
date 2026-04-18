# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/unit_selector.py
功能說明 (Description): 單元 → 題型 pattern skill 選擇器
根據單元 (curriculum, volume, chapter) 查詢該單元下所有 pattern skills，
並以權重抽樣回傳一個 skill_id 供出題使用。

[架構] 一單元多題型、一題型一 skill 檔
- 單元 = (curriculum, volume, chapter[, section])
- 題型 = pattern skill（獨立 skill_id、獨立 skills/<skill_id>.py）
- 選擇策略：權重抽樣（可擴充為自適應）
=============================================================================
"""

import os
import json
import random
from typing import Optional

# Lazy import to avoid circular dependency
def _get_db():
    from models import db
    from flask import has_request_context
    if has_request_context():
        from flask import current_app
        with current_app.app_context():
            pass
    return db

def _get_project_root():
    """專案根目錄"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def _skill_file_exists(skill_id: str) -> bool:
    """檢查 skills/<skill_id>.py 是否存在"""
    root = _get_project_root()
    path = os.path.join(root, 'skills', f"{skill_id}.py")
    return os.path.isfile(path)


def _load_unit_weights() -> dict:
    """
    載入 unit_pattern_config.json。
    讀取順序：instance/（覆蓋）→ config/（進 git 的基準版）
    """
    root = _get_project_root()
    path = None
    for rel in ['instance', 'config']:
        p = os.path.join(root, rel, 'unit_pattern_config.json')
        if os.path.isfile(p):
            path = p
            break
    if not path:
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _make_unit_key(curriculum: str, volume: str, chapter: str) -> str:
    """產生 unit 的鍵值，用於查詢設定檔"""
    return f"{curriculum}|{volume}|{chapter}"


def select_pattern_skill_for_unit(
    curriculum: str,
    volume: str,
    chapter: str,
    weights_config: Optional[dict] = None
) -> Optional[str]:
    """
    根據單元資訊選出一個 pattern skill_id。
    
    Args:
        curriculum: 課綱 (e.g. junior_high, general)
        volume: 冊別 (e.g. 數學2上)
        chapter: 章節名稱 (e.g. 第二章 二次方根與畢氏定理)
        weights_config: 可選，外部傳入的權重設定；若為 None 則從 unit_pattern_config.json 載入
    
    Returns:
        選中的 skill_id，若無可選 skill 則回傳 None
    
    選擇邏輯：
        1. 若 unit_pattern_config.json 有定義該 unit 的 pattern skills 與權重，依權重抽樣
        2. 否則從 skill_curriculum 查詢該 (curriculum, volume, chapter) 下的所有 skill_id，等權抽樣
        3. 過濾僅保留 skills_info 中 is_active 且 skills/<skill_id>.py 存在的
    """
    unit_key = _make_unit_key(curriculum, volume, chapter)
    
    # 1. 嘗試從設定檔取得 pattern skills 與權重
    if weights_config is None:
        weights_config = _load_unit_weights()
    
    configured = weights_config.get(unit_key)
    if configured and isinstance(configured, list):
        items = [x for x in configured if isinstance(x, dict) and x.get('skill_id')]
        if items:
            # 過濾：僅保留 skills/<skill_id>.py 存在的
            valid_items = [x for x in items if _skill_file_exists(x['skill_id'])]
            if not valid_items:
                return None
            weights = [float(x.get('weight', 1)) for x in valid_items]
            skill_ids = [x['skill_id'] for x in valid_items]
            return random.choices(skill_ids, weights=weights, k=1)[0]
    
    # 2. Fallback: 從 skill_curriculum 查詢
    try:
        from models import db, SkillCurriculum, SkillInfo
        
        rows = db.session.query(SkillCurriculum.skill_id).filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.chapter == chapter
        ).distinct().all()
        
        skill_ids = [r[0] for r in rows if r[0]]
        if not skill_ids:
            return None
        
        # 過濾：僅保留 is_active、skills_info 存在、且 skills/<id>.py 存在
        active = db.session.query(SkillInfo.skill_id).filter(
            SkillInfo.skill_id.in_(skill_ids),
            SkillInfo.is_active == True
        ).all()
        valid_ids = [a[0] for a in active if _skill_file_exists(a[0])]
        if not valid_ids:
            valid_ids = [sid for sid in skill_ids if _skill_file_exists(sid)]
        
        return random.choice(valid_ids) if valid_ids else None
    except Exception:
        return None


def get_unit_pattern_skills(
    curriculum: str,
    volume: str,
    chapter: str,
    weights_config: Optional[dict] = None
) -> list:
    """
    取得單元下所有 pattern skills 與權重，供管理/配置頁面使用。
    
    Returns:
        [{"skill_id": str, "weight": float, "source": "config"|"db"}, ...]
    """
    unit_key = _make_unit_key(curriculum, volume, chapter)
    
    if weights_config is None:
        weights_config = _load_unit_weights()
    
    configured = weights_config.get(unit_key)
    if configured and isinstance(configured, list):
        return [
            {"skill_id": x.get('skill_id'), "weight": float(x.get('weight', 1)), "source": "config"}
            for x in configured if isinstance(x, dict) and x.get('skill_id')
        ]
    
    try:
        from models import db, SkillCurriculum, SkillInfo
        
        rows = db.session.query(SkillCurriculum.skill_id).filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.chapter == chapter
        ).distinct().all()
        
        return [
            {"skill_id": r[0], "weight": 1.0, "source": "db"}
            for r in rows if r[0]
        ]
    except Exception:
        return []
