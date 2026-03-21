# -*- coding: utf-8 -*-
"""
技能顯示策略：依 skill_id 回傳該技能的顯示/格式化設定。
供 live_show_healer 等模組使用。
"""

def get_skill_policy(skill_id):
    """
    取得指定 skill 的策略設定。
    
    Returns:
        dict: {
            "enable_fraction_display": bool,   # 是否啟用分數顯示
            "force_fraction_answer": bool,    # 是否強制答案為分數格式
            ...
        }
    """
    # 可從 agent_skills/<skill_id>/skill.json 或 DB 讀取；暫用預設
    _DEFAULTS = {
        "enable_fraction_display": False,
        "force_fraction_answer": False,
    }
    # 依 need 可擴充 skill 專屬 overrides
    overrides = {}
    policy = _DEFAULTS.copy()
    policy.update(overrides.get(str(skill_id), {}))
    return policy
