# -*- coding: utf-8 -*-
"""
=============================================================================
Module Name: cleanup_project.py
Description: 專案根目錄自動清理與維護工具 (Project Root Directory Cleanup Tool)
             此工具專為 Flask 數學專案開發，旨在解決開發過程中產生的臨時測試檔堆積問題。

功能詳解:
    1. 目錄隔離：自動偵測並建立 /temp 資料夾，將雜亂檔案集中管理。
    2. 特徵識別：透過檔名前綴 (add_, debug_, fix_, 等) 與檔案模式識別非核心腳本。
    3. 安全防護：設定嚴格的白名單，確保 app.py, models.py 及核心資料夾 (core/) 不被變動。
    4. 衝突處理：若目標目錄已存在同名檔案，會自動加上時間戳記避免內容覆蓋。
    5. 操作追蹤：於 /temp 目錄生成 moved_log.txt，詳列所有檔案搬移紀錄，方便日後取回。
    6. 清理環境：執行 python cleanup_project.py
版本資訊: V1.0 (Refactored Branch Standard)
更新日期: 2026-01-13
=============================================================================
"""

import os
import shutil
from datetime import datetime

# ==========================================
# 1. 安全白名單設定 (絕對不可移動)
# ==========================================
# 核心檔案
PROTECTED_FILES = [
    'app.py', 'config.py', 'models.py', 'manage.py', 
    '.env', '.gitignore', 'requirements.txt', 'LICENSE'
]
# 核心資料夾
PROTECTED_DIRS = [
    'core', 'static', 'templates', 'datasource', 
    'venv', 'skills', 'migrations', '.git', 'temp'
]

# ==========================================
# 2. 臨時檔案特徵設定 (識別移動對象)
# ==========================================
# 依據截圖中發現的雜亂前綴
TEMP_PREFIXES = [
    'add_', 'apply_', 'check_', 'debug_', 'fix_', 
    'create_', 'analyze_', 'dump_', 'find_', 'cleanup_', 
    'change_', 'final_', 'tmp_', 'test_', 'run_'
]

# 目標存放目錄
TEMP_DIR = 'temp'

def cleanup():
    print(f"--- 啟動專案清理作業 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    
    # 建立目標資料夾
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        print(f"[*] 建立目錄: {TEMP_DIR}")

    moved_count = 0
    log_entries = []
    
    # 掃描根目錄
    for filename in os.listdir('.'):
        # 排除白名單目錄與檔案
        if os.path.isdir(filename) or filename in PROTECTED_FILES:
            continue
            
        # 識別邏輯
        is_temp = any(filename.startswith(pre) for pre in TEMP_PREFIXES) or \
                  (filename.endswith('.py') and ('_v2' in filename or '_v1' in filename)) or \
                  filename in ['cmd.txt', 'desktop.ini', 'temp.txt']

        if is_temp:
            src = filename
            dst_path = os.path.join(TEMP_DIR, filename)
            
            # 檔名重複處理
            if os.path.exists(dst_path):
                base, ext = os.path.splitext(filename)
                dst_path = os.path.join(TEMP_DIR, f"{base}_{datetime.now().strftime('%H%M%S')}{ext}")

            try:
                shutil.move(src, dst_path)
                msg = f"已移動: {src} -> {TEMP_DIR}/"
                print(msg)
                log_entries.append(f"{datetime.now()}: {src} -> {dst_path}")
                moved_count += 1
            except Exception as e:
                print(f"[!] 移動 {src} 失敗: {e}")

    # 寫入日誌檔
    log_file = os.path.join(TEMP_DIR, 'moved_log.txt')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n--- 清理紀錄 {datetime.now()} ---\n")
        f.write("\n".join(log_entries) + "\n")
    
    print("-" * 50)
    print(f"清理完成！共安全移除了 {moved_count} 個腳本檔案。")
    print(f"詳細清單請參閱: {log_file}")

if __name__ == "__main__":
    cleanup()