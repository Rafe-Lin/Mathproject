# -*- coding: utf-8 -*-
# ==============================================================================
# ID: validate_code.py
# Version: V2.1.0 (Legacy Validator)
# Last Updated: 2026-02-17
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   本程式是一個輕量級的代碼驗證工具，用於快速測試 Prompt 的生成品質。
#   與 benchmark.py 相比，它不計算複雜的 MCRI 分數，僅檢查是否能成功執行 (Pass/Fail)。
#   適合在 Prompt 開發階段進行快速迭代測試。
#
# [Scientific Control Strategy]:
#   - 採用簡化的驗證流程：Syntax Check + Execution Check。
#
# [Database Schema Usage]:
#   1. Read: evals.json
#   2. Read: PROMPT_DIR (golden_prompts)
#
# [Logic Flow]:
#   1. Load Evals         -> 讀取測試清單。
#   2. Loop Tests         -> 對每個案例執行 N 次 (Run Count)。
#   3. AI & Heal          -> 生成代碼並執行 Regex Healer (預設)。
#   4. Fast Validation    -> 檢查 Python 語法與執行狀態。
#   5. Statistics         -> 計算並輸出簡易的通過率報告。
# ==============================================================================
import sys
import os
import json
import time
import subprocess
import ast
from typing import Dict, List, Tuple

# 設定專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

try:
    from core.validators.code_validator import validate_python_code
    from core.healers.regex_healer import RegexHealer
    from core.healers.ast_healer import ASTHealer
    print("Core modules loaded successfully.")
except ImportError as e:
    print(f"Warning: Failed to import core modules: {e}")
    print("Make sure this script is run from the project root or adjust sys.path.")

# 預設路徑（可從命令列參數覆蓋）
EVALS_PATH = os.path.join(PROJECT_ROOT, "math-problem-generator", "evals", "evals.json")
PROMPT_DIR = os.path.join(PROJECT_ROOT, "experiments", "golden_prompts")

def load_evals() -> List[Dict]:
    """讀取 evals.json"""
    if not os.path.exists(EVALS_PATH):
        raise FileNotFoundError(f"evals.json not found at {EVALS_PATH}")
    
    with open(EVALS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("evals", [])

def run_single_test(prompt_file: str, eval_case: Dict) -> Tuple[bool, str, float]:
    """執行單一測試案例"""
    start_time = time.time()
    
    try:
        # 讀取 Prompt
        prompt_path = os.path.join(PROMPT_DIR, prompt_file)
        if not os.path.exists(prompt_path):
            return False, f"Prompt file not found: {prompt_path}", time.time() - start_time
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        
        # 模擬 AI 生成（這裡用你的實際 AI 呼叫函數）
        # 假設你有 call_ai_with_retry(prompt) 函數
        raw_code = call_ai_with_retry(prompt)  # 請替換成你們的真實函數
        
        # 執行 Healer（可選）
        regex_healer = RegexHealer()
        healed_code, fixes = regex_healer.heal(raw_code)
        
        # 驗證
        is_valid, error_msg = validate_python_code(healed_code)
        
        duration = time.time() - start_time
        status_msg = "PASS" if is_valid else f"FAIL: {error_msg}"
        
        return is_valid, status_msg, duration
    
    except Exception as e:
        duration = time.time() - start_time
        return False, f"Runtime Error: {str(e)}", duration

def run_benchmark(run_count: int = 3):
    """執行完整 Benchmark"""
    print("🚀 Starting Math Problem Generator Benchmark...")
    print(f"Evals path: {EVALS_PATH}")
    
    evals = load_evals()
    if not evals:
        print("No evaluations found.")
        return
    
    results = {}
    total_pass = 0
    total_tests = 0
    
    for eval_case in evals:
        eval_id = eval_case["eval_id"]
        prompt_file = eval_case["prompt_file"]
        desc = eval_case.get("description", "")
        
        print(f"\n[{eval_id}] {desc}")
        print("-" * 50)
        
        success_count = 0
        times = []
        
        for attempt in range(1, run_count + 1):
            print(f"  Attempt {attempt}/{run_count}...")
            is_pass, msg, duration = run_single_test(prompt_file, eval_case)
            
            if is_pass:
                success_count += 1
                print(f"  PASS ({duration:.2f}s)")
            else:
                print(f"  FAIL ({duration:.2f}s): {msg}")
            
            times.append(duration)
        
        pass_rate = (success_count / run_count) * 100
        avg_time = sum(times) / len(times) if times else 0
        
        results[eval_id] = {
            "pass_rate": pass_rate,
            "success_count": success_count,
            "total": run_count,
            "avg_time": avg_time
        }
        
        total_pass += success_count
        total_tests += run_count
    
    # 總結報告
    overall_pass_rate = (total_pass / total_tests) * 100 if total_tests > 0 else 0
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"Total Evaluations: {len(evals)}")
    print(f"Total Runs: {total_tests}")
    print(f"Overall Pass Rate: {overall_pass_rate:.1f}%")
    
    for eval_id, res in results.items():
        print(f"{eval_id}: {res['pass_rate']:.1f}% ({res['success_count']}/{res['total']}) | Avg Time: {res['avg_time']:.2f}s")

if __name__ == "__main__":
    run_benchmark(run_count=3)  # 每道 eval 跑 3 次取平均