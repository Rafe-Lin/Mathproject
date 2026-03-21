# -*- coding: utf-8 -*-
# ==============================================================================
# ID: core/code_utils/file_utils.py
# Version: V2.0 (Refactored from code_generator.py)
# Last Updated: 2026-01-30
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   檔案系統相關工具函數
#   提供路徑處理和目錄創建功能
#
# [Functionality]:
#   1. get_base_root: 取得專案根目錄（優先使用 Flask app context）
#   2. path_in_root: 構建專案根目錄下的路徑
#   3. ensure_dir: 確保目錄存在（不存在則創建）
#
# [Logic Flow]:
#   get_base_root -> Flask context 或 fallback to parent of core/
#   path_in_root -> os.path.join(base_root, *parts)
#   ensure_dir -> os.makedirs(path, exist_ok=True)
# ==============================================================================

import os

# 保持原函數名（移除前綴下劃線，讓外部可調用）
def get_base_root():
    """
    優先用 Flask current_app.root_path；若不可用，回退到 core/ 的上一層（專案根）
    """
    try:
        from flask import has_app_context, current_app
        if has_app_context():
            return current_app.root_path
    except Exception:
        pass
    # fallback: project root = parent of core/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

def path_in_root(*parts):
    """構建專案根目錄下的路徑"""
    return os.path.join(get_base_root(), *parts)

def ensure_dir(p):
    """確保目錄存在"""
    os.makedirs(p, exist_ok=True)
    return p
