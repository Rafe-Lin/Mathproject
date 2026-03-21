# -*- coding: utf-8 -*-
"""
Math-Master: AI-Driven Education Platform (2026 YC-Awards Project)
Module: Environment Sanitizer & Aseptic Bootloader
-------------------------------------------------------------------------
【功能描述】
本腳本為 Math-Master 專案的「核心啟動器」。其主要任務是實施「環境無菌化 (Aseptic Booting)」，
解決 Large Language Models (LLM) 在 JIT (Just-in-Time) 代碼生成過程中常見的
「指令污染 (Instruction Pollution)」與「模組快取 (Module Caching)」問題。

【核心技術亮點】
1. 物理隔離 (Physical Isolation): 強制清空所有動態生成的 Python 腳本，防止舊題型邏輯殘留。
2. 顯存重置 (VRAM Reset): 透過 Ollama API 強制卸載模型，抹除 5060 Ti 上的視覺上下文快取。
3. 零快取啟動 (Zero-Cache Execution): 禁用 Python 的 pyc 編譯機制，確保每一行代碼都是即時解析。
-------------------------------------------------------------------------
Author: Math-Master Dev Team
Date: 2026-02-28
"""

import os
import shutil
import sys
import subprocess
import time

def sanitize_environment():
    # 設置標題裝飾
    print("="*60)
    print("      Math-Master 2026 - 環境無菌化啟動程序啟動中...")
    print("="*60)

    # 0. 通訊埠淨空防禦機制 (專門針對 Windows 系統)
    # 目的：防止因為 VSCode 當掉或 Flask 不正常中斷，導致舊的 python.exe 依然死咬著 5000 Port
    print("\n🛡️ [Step 0/4] 正在掃描並強制釋放本地通訊埠 (Port 5000)...")
    try:
        # 尋找監聽 5000 Port 的 PID
        # netstat -ano 的格式通常為: TCP    127.0.0.1:5000     0.0.0.0:0              LISTENING       12345
        cmd_find = 'netstat -ano | findstr :5000'
        result = subprocess.run(cmd_find, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            pids_killed = set()
            for line in lines:
                parts = line.strip().split()
                # 確保我們抓的是監聽中，且拿到最後面的一組數字 (PID)
                if len(parts) >= 5 and 'LISTENING' in parts:
                    pid = parts[-1]
                    if pid != '0' and pid not in pids_killed:
                        print(f"   >>> 發現殭屍程序 (PID: {pid}) 佔用了通訊埠，執行斬首行動...")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True, text=True)
                        pids_killed.add(pid)
            if pids_killed:
                print(f"   >>> 成功肅清了 {len(pids_killed)} 個頑強霸佔 5000 port 的進程。")
            else:
                print("   >>> Port 5000 目前淨空無礙。")
        else:
            print("   >>> Port 5000 目前淨空無礙。")
    except Exception as e:
        print(f"   >>> [警報] 通訊埠釋放檢測失敗: {e}")

    # 1. 清理 Python 字節碼快取
    # 目的：防止 Python 執行舊版編譯後的 .pyc 檔案，確保新邏輯立即生效
    print("\n🧹 [Step 1/4] 正在掃描並清理 Python 檔案快取 (__pycache__)...")
    cache_count = 0
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                cache_count += 1
    print(f"   >>> 成功清理 {cache_count} 個快取節點，確保邏輯純淨。")

    # 2. 初始化 JIT 存儲空間
    # 目的：移除所有舊的 generate_live_xxx.py，保證演示現場只會看到最新的題目腳本
    print("\n🗑️ [Step 2/4] 正在重置 JIT 動態程式碼儲存區 (generated_scripts)...")
    gen_path = "./generated_scripts"
    if os.path.exists(gen_path):
        shutil.rmtree(gen_path)
    os.makedirs(gen_path, exist_ok=True)
    print("   >>> 資料夾已完成物理重置，防止「舊模板污染」現象發生。")

    # 3. 釋放 GPU 顯存與上下文記憶
    # 目的：重啟 Qwen3-VL 的神經元狀態，避免它「記得」之前的絕對值題目
    print("\n🧠 [Step 3/4] 正在對 RTX 5060 Ti 執行顯存重置 (VRAM Reset)...")
    try:
        # 取得所有正在執行的模型清單
        ps_result = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        lines = ps_result.stdout.strip().split('\n')
        
        stopped_models = []
        if len(lines) > 1:
            # 第一行通常是標題 (NAME ID SIZE PROCESSOR UNTIL...)
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    # 強制停止模型以清空 Ollama 內部的 Context Window
                    subprocess.run(["ollama", "stop", model_name], capture_output=True)
                    stopped_models.append(model_name)
                    
        if stopped_models:
            print(f"   >>> 已強制卸載以下模型：{', '.join(stopped_models)}")
            print("   >>> 視覺記憶區(Vision Context)與顯存已完全清空。")
        else:
            print("   >>> 目前沒有正在執行的 Ollama 模型。")
            
    except Exception as e:
        print(f"   >>> [警報] 顯存重置失敗，請確認 Ollama 服務是否正常啟動。錯誤訊息: {e}")

    # 4. 啟動 Web 核心
    # 目的：以 -B 參數啟動，徹底停用 Python 的寫入快取行為
    print("\n🚀 [Step 4/4] 正在以『零快取模式 (Zero-Cache Mode)』啟動 Flask 核心...")
    print("-" * 60)
    print("【系統狀態】後端服務即將於 127.0.0.1:5000 運行。")
    print("【特別指示】演示期間請勿手動修改 generated_scripts 內容。")
    print("-" * 60 + "\n")

    # 延遲 1 秒確保所有資源釋放完畢
    time.sleep(1)

    # 使用 sys.executable 確保使用當前環境的 Python
    # -B 參數：不寫入 .pyc 檔案
    # -u 參數：強制標準輸出 (stdout) 不緩衝，方便即時觀察 AI 日誌
    try:
        subprocess.run([sys.executable, "-B", "-u", "app.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 [系統停止] Math-Master 已安全關閉。")

if __name__ == "__main__":
    sanitize_environment()