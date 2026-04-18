#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================== 
# ID: code_generator.py
# Version: V50.0 (Semantic Self-Correction Edition)
# Last Updated: 2026-02-06
# Author: Math AI Research Team (Advisor & Student)
#
# [Description]:
#   本模組為科展實驗的自動技能生成核心，負責根據規格書自動產生技能程式碼，
#   並支援 AST/Regex 修復、Semantic Self-Correction (Hybrid Healer)、沙盒驗證等功能，確保生成結果符合標準。
#
#   [Scientific Control Strategy]:
#   本模組配合「單一黃金標準」策略，確保所有技能生成均以統一規格書為依據，
#   以利不同模型、Ablation 組別間的公平比較與統計分析。
#
# [Key Functions]:
#   1. auto_generate_skill_code: 主入口，根據技能 ID 與實驗參數自動生成技能程式碼。
#   2. ast_fix_code: 進行 AST 結構修復，提升程式碼健壯性。
#   3. validate_skill_code: 執行沙盒驗證，確保生成程式碼可正確運作。
#
# [Database Schema Usage]:
#   - 讀取: SkillGenCodePrompt (獲取標準規格書)
#   - 寫入: experiment_log (記錄生成過程與修復次數)
#   - 寫入: Local File System (儲存最終技能程式碼)
#
# [Logic Flow]:
#   1. 讀取目標技能規格書
#   2. 生成初版程式碼
#   3. 執行 AST/Regex 修復（依 Ablation 設定）
#   4. 沙盒驗證與評分
#   5. 寫入實驗日誌與技能檔案
# ============================================================================== 

import os
import time
import datetime
import re
import textwrap
import importlib.util
import sqlite3
import random
import math
import ast
import operator
from fractions import Fraction
from pathlib import Path

# Local Imports
# (Ensure PYTHONPATH includes the project root)
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from core.ai_wrapper import get_ai_client, call_ai_with_retry
from models import SkillGenCodePrompt, ExperimentLog, db, SkillInfo, TextbookExample, AblationSetting

from core.healers.regex_healer import RegexHealer
from core.healers.ast_healer import ASTHealer
from core.healers.unified_cleanup_healer import heal_unified
from core.prompts.prompt_builder import PromptBuilder
from core.validators.code_validator import validate_python_code as _validate_python_code
from core.validators.dynamic_sampler import DynamicSampler
from core.code_utils.file_utils import ensure_dir, path_in_root
from core.code_utils.math_utils import *
from core.code_utils.latex_utils import *

REFACTOR_MODULES_AVAILABLE = True


def fix_code_via_ast(code_str: str, ai_client=None):
    """Backward-compatible wrapper used by older tests and tooling."""
    healer = ASTHealer(ai_client=ai_client)
    return healer.heal(code_str)

def _inject_domain_libs(code_str, skill_id: str | None = None):
    """
    [New Feature 2026-02-16] 自動注入 Domain Libraries (如 RadicalOps) 的完整實作
    使生成的 Skill File 可以獨立運行 (Self-Contained)。
    [Fix V2] 增強版：
    1. 強制替換 Stub
    2. 自動注入 Global Alias (simplify_term = RadicalOps.simplify_term)
    3. 自動移除錯誤的 import (from RadicalOps import ...)
    [Phase 4-B] 若提供 skill_id，從 skill.json["injected_apis"] 強制注入宣告的 API，
    防止 AI 忘記使用 class name 時的靜默失敗。
    """
    injected_names = []

    # ── Phase 4-B: read declared APIs + required_imports from skill.json ──
    declared_apis: list[str] = []
    required_imports: list[str] = []
    if skill_id:
        try:
            import json as _json, glob as _glob
            project_root = os.path.dirname(os.path.abspath(__file__))
            pattern = os.path.join(project_root, "..", "agent_skills", skill_id, "skill.json")
            manifest_candidates = _glob.glob(pattern)
            if not manifest_candidates:
                # try walking up one more level
                pattern2 = os.path.join(project_root, "agent_skills", skill_id, "skill.json")
                manifest_candidates = _glob.glob(pattern2)
            if manifest_candidates:
                with open(manifest_candidates[0], encoding="utf-8") as fh:
                    meta = _json.load(fh)
                declared_apis = [str(a) for a in (meta.get("injected_apis") or []) if a]
                required_imports = [str(m) for m in (meta.get("required_imports") or []) if m]
        except Exception:
            pass
    # ───────────────────────────────────────────────────────────────────────

    # 補齊 required_imports（如 random、math）— 若程式碼未有 import 則在頂端補上
    import_lines_to_add = []
    for mod in required_imports:
        pattern_found = re.search(rf'^\s*import\s+{re.escape(mod)}\b', code_str, re.MULTILINE)
        if not pattern_found:
            import_lines_to_add.append(f"import {mod}")
    if import_lines_to_add:
        code_str = "\n".join(import_lines_to_add) + "\n" + code_str
    
    # 定義需要注入的 Libs 關鍵字與對應 Class Name
    target_libs = {
        'RadicalOps': 'RadicalOps',
        'IntegerOps': 'IntegerOps',
        'FractionOps': 'FractionOps',
        'PolynomialOps': 'PolynomialOps'
    }

    if (
        skill_id
        and "OfPolynomial" in skill_id
        and "PolynomialOps" not in code_str
        and re.search(r'(?<!\.)\b(add|sub|mul|normalize|format_plain|format_latex|random_poly)\s*\(', code_str)
    ):
        code_str = "# [skill.json declared: PolynomialOps]\n" + code_str

    # 強制注入 skill.json 宣告的 APIs（即使 code_str 未引用）
    for api in declared_apis:
        if api in target_libs and api not in code_str:
            code_str = f"# [skill.json declared: {api}]\n" + code_str
    
    # 讀取 domain_function_library.py 作為 Class 定義的統一來源
    try:
        libs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prompts', 'domain_function_library.py')
        if not os.path.exists(libs_path):
            # Fallback to legacy domain_libs.py
            libs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scaffold', 'domain_libs.py')
        if not os.path.exists(libs_path):
            return code_str, []
            
        with open(libs_path, 'r', encoding='utf-8') as f:
            libs_source = f.read()
    except Exception:
        return code_str, []

    # 解析 libs_source，提取各個 Class 的定義
    feature_code = ""

    for keyword, class_name in target_libs.items():
        # 檢查目標代碼是否使用了該 Lib
        if keyword in code_str:
            # 0. 清理錯誤的 import 語句 (e.g., from RadicalOps import ...)
            # 因為我們將把 RadicalOps 注入到檔案內，這些 import 是多餘且會報錯的
            invalid_import_pattern = re.compile(rf'^\s*from\s+{class_name}\s+import.*$', re.MULTILINE)
            if invalid_import_pattern.search(code_str):
                code_str = invalid_import_pattern.sub(f"# [Removed Invalid Import] {class_name} is injected internally.", code_str)

            # 1. 如果代碼中已有該 class 的定義 (Stub 或完整定義)，先移除它
            # Pattern: class ClassName ... (直到下一個 class 或特殊標記)
            remove_pattern = re.compile(
                rf'(class {class_name}[^:]*:(?:.|\n)*?)(?=\nclass |\ndef |\n# \[|\n[A-Z_]{{3,}}\s*=|\Z)',
                re.MULTILINE,
            )
            
            if remove_pattern.search(code_str):
                code_str = remove_pattern.sub('', code_str)
            
            # 2. 從 libs_source 提取該 Class 的完整源碼
            # Stop not only at the next class, but also at top-level string constant assignments
            # (e.g. FRACTIONOPS_HELPERS = r""" ...) which appear in domain_function_library.py.
            extract_pattern = re.compile(
                rf'(class {class_name}:.*?)(\nclass |\n[A-Z_]{{3,}}\s*=\s*r?"""|\Z)',
                re.DOTALL
            )
            match = extract_pattern.search(libs_source)
            if match:
                class_code = match.group(1).strip()
                
                # 3. 準備注入內容 (包含 Header 和 Global Alias)
                header = f"\n# ==============================================================================\n" \
                         f"# [AUTO-INJECTED RESOURCE] {class_name}\n" \
                         f"# ==============================================================================\n"
                
                # 自動產生 Global Alias (方便 AI 直接呼叫 simplify_term)
                # 只有 RadicalOps 需要這個特殊處理
                aliases = ""
                if class_name == 'RadicalOps':
                    aliases = "\n\n# [Global Aliases for AI Convenience]\n" \
                              "simplify_term = RadicalOps.simplify_term\n" \
                              "format_term = RadicalOps.format_term\n" \
                              "format_term_unsimplified = RadicalOps.format_term_unsimplified\n" \
                              "format_expression = RadicalOps.format_expression\n" \
                              "add_dicts = RadicalOps.add_dicts\n" \
                              "multiply_dicts = RadicalOps.multiply_dicts\n"
                elif class_name == 'PolynomialOps':
                    aliases = "\n\n# [Global Aliases for PolynomialOps]\n" \
                              "poly_normalize = PolynomialOps.normalize\n" \
                              "poly_format_latex = PolynomialOps.format_latex\n" \
                              "poly_format_plain = PolynomialOps.format_plain\n" \
                              "poly_add = PolynomialOps.add\n" \
                              "poly_sub = PolynomialOps.sub\n" \
                              "poly_mul = PolynomialOps.mul\n" \
                              "poly_random = PolynomialOps.random_poly\n" \
                              "normalize = PolynomialOps.normalize\n" \
                              "format_latex = PolynomialOps.format_latex\n" \
                              "format_plain = PolynomialOps.format_plain\n" \
                              "add = PolynomialOps.add\n" \
                              "sub = PolynomialOps.sub\n" \
                              "mul = PolynomialOps.mul\n" \
                              "random_poly = PolynomialOps.random_poly\n"
                
                feature_code += f"{header}{class_code}{aliases}\n"
                injected_names.append(class_name)
    
    if feature_code:
        # 將注入的代碼插入到 [DOMAIN HELPERS] 標記處
        # 如果找不到標記，插在 import 之後
        insert_marker = "# [DOMAIN HELPERS"
        if insert_marker in code_str:
             # 插在標記後面
             lines = code_str.split('\n')
             for i, line in enumerate(lines):
                 if insert_marker in line:
                     lines.insert(i + 1, feature_code)
                     break
             code_str = '\n'.join(lines)
        else:
            # Fallback
            insert_marker_ai = "# [AI GENERATED CODE]"
            if insert_marker_ai in code_str:
                code_str = code_str.replace(insert_marker_ai, f"{feature_code}\n\n{insert_marker_ai}")
            else:
                last_import = -1
                lines = code_str.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        last_import = i
                lines.insert(last_import + 1, feature_code)
                code_str = '\n'.join(lines)
            
    return code_str, injected_names

# ==============================================================================
# Healer Pipeline Logging Configuration
# ==============================================================================
DEBUG_MODE = os.getenv('HEALER_DEBUG', '0') == '1'
VERBOSE_LEVEL = int(os.getenv('HEALER_VERBOSE', '2'))  # 0=minimal, 1=normal, 2=detailed (預設詳細版)

def log_pipeline_header(skill_id, ablation_id, ablation_name):
    """列印 Pipeline 啟動標題"""
    if VERBOSE_LEVEL == 0:
        return
    
    if VERBOSE_LEVEL >= 1:
        print(f"\n╔════════════════════════════════════════════════════════════╗")
        print(f"║  🔬 Code Generation & Healing Pipeline                     ║")
        print(f"║  Skill: {skill_id:<48} ║")
        print(f"║  Ablation: Ab{ablation_id} ({ablation_name:<38}) ║")
        print(f"╚════════════════════════════════════════════════════════════╝\n")

def log_step_start(step_num, step_name, description=""):
    """列印步驟開始"""
    if VERBOSE_LEVEL == 0:
        return
    
    if VERBOSE_LEVEL == 1:
        print(f"\n【Step {step_num}】{step_name}")
    elif VERBOSE_LEVEL == 2:
        print(f"\n┌─ Step {step_num}: {step_name} {'─' * (48 - len(step_name))}┐")
        if description:
            print(f"│ {description}")

def log_step_result(step_num, fixes, extra_info=""):
    """列印步驟結果"""
    if VERBOSE_LEVEL == 0:
        return
    
    if VERBOSE_LEVEL == 1:
        print(f"   📊 {extra_info}: {fixes} 項修復")
    elif VERBOSE_LEVEL == 2:
        print(f"│ ")
        print(f"│ 📊 結果: {fixes} 項修復 | {extra_info}")
        print(f"└{'─' * 58}┘")

def log_fix_detail(check_name, status, detail=""):
    """列印修復細節"""
    if VERBOSE_LEVEL < 2:
        return
    
    status_icon = "✅" if status == "fixed" else "○" if status == "skip" else "⚠️"
    print(f"│ {status_icon} {check_name:<30} {detail}")

def log_pipeline_summary(total_fixes, status, duration):
    """列印 Pipeline 總結（含詳細修復統計）"""
    if VERBOSE_LEVEL == 0:
        print(f"  ✅ {status} | 總修復: {total_fixes}")
        return
    
    if VERBOSE_LEVEL >= 1:
        # 解析修復統計（例如：Basic=1, Regex=3, AST=0）
        try:
            parts = total_fixes.split(", ")
            basic_count = int(parts[0].split("=")[1])
            regex_count = int(parts[1].split("=")[1])
            ast_count = int(parts[2].split("=")[1])
            total_count = basic_count + regex_count + ast_count
            
            # 構建詳細統計字串
            stats_line = f"Basic={basic_count}, Regex={regex_count}, AST={ast_count} | 總計={total_count}"
        except:
            # Fallback: 使用原始字串
            stats_line = total_fixes
            total_count = 0
        
        print(f"\n╔════════════════════════════════════════════════════════════╗")
        
        # 根據狀態選擇圖標
        if status == "PASSED":
            status_icon = "✅ Pipeline 執行成功"
        else:
            status_icon = "❌ Pipeline 執行失敗"
        
        print(f"║  {status_icon:<56} ║")
        print(f"║  {'':<58} ║")
        
        # [2026-02-01 新增] 詳細修復統計（Ab3 特別關注）
        if total_count > 0:
            print(f"║  📊 修復統計（分階段累計）:{'':<33} ║")
            print(f"║     • Basic Cleanup:    {basic_count} 項{'':<34} ║")
            print(f"║     • Regex Healer:     {regex_count} 項{'':<34} ║")
            print(f"║     • AST Healer:       {ast_count} 項{'':<35} ║")
            print(f"║     • 總計修復:         {total_count} 項{'':<34} ║")
        else:
            print(f"║  📊 修復統計: 無需修復（代碼完美生成）{'':<23} ║")
        
        print(f"║  {'':<58} ║")
        print(f"║  驗證狀態: {status:<47} ║")
        print(f"║  總耗時: {duration:.2f}s{' ' * (47 - len(f'{duration:.2f}s'))}║")
        print(f"╚════════════════════════════════════════════════════════════╝\n")


def _build_prompt(skill_id, ablation_id, db_master_spec, use_golden_prompt=False, save_golden_prompt=False):
    """根據 ablation_id 構建 prompt (委派給 PromptBuilder 或讀取 Golden Prompt)
    
    Args:
        skill_id: 技能 ID
        ablation_id: Ablation 層級 (1/2/3)
        db_master_spec: 數據庫中的規格書（Fallback 使用）
        use_golden_prompt: 是否使用固定的 Golden Prompt（實驗模式 2）
        save_golden_prompt: 是否將生成的 Prompt 保存為 Golden Prompt（實驗模式 4）
    """
    
    # [實驗模式 2] 讀取固定的 Golden Prompt
    if use_golden_prompt:
        # Ab2/Ab3 共用同一個 Ab2 Prompt（因為差異只在 Healer 開關）
        prompt_ablation_id = 1 if ablation_id == 1 else 2
        golden_prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'experiments', 'golden_prompts', 'temp', 
            f'{skill_id}_Ab{prompt_ablation_id}.txt'
        )
        
        if os.path.exists(golden_prompt_path):
            try:
                with open(golden_prompt_path, 'r', encoding='utf-8') as f:
                    prompt = f.read()
                
                if VERBOSE_LEVEL >= 1:
                    print(f"   📄 已讀取 Golden Prompt: {os.path.basename(golden_prompt_path)}")
                
                # 返回 Golden Prompt（topic 和 textbook_example 不重要了）
                return prompt, "", ""
            except Exception as e:
                if VERBOSE_LEVEL >= 1:
                    print(f"   ⚠️ 無法讀取 Golden Prompt ({e})，改用動態生成")
        else:
            if VERBOSE_LEVEL >= 1:
                print(f"   ⚠️ Golden Prompt 不存在: {golden_prompt_path}")
                print(f"   → 改用動態生成模式")
    
    # [V2.5 新增] 動態提取課本範例（對所有 Ablation ID）
    textbook_example = ""
    topic = ""
    
    # 從數據庫獲取課本範例（只取序號最小的第一個）
    example = TextbookExample.query.filter_by(skill_id=skill_id).order_by(TextbookExample.id.asc()).first()
    
    if example:
        # 只使用第一個例題，不合併多個
        if example.problem_text:
            textbook_example = f"範例：{example.problem_text}"
        else:
            textbook_example = "範例：請生成類似的數學題目"
        
        # 從 skill_id 提取主題 (例如: gh_ApplicationsOfDerivatives → 導數的應用)
        # 簡化處理：直接使用 skill_id 的可讀部分
        if "_" in skill_id:
            topic_part = skill_id.split("_")[-1]
            # 將 CamelCase 轉為可讀文字
            topic = "".join([" " + c if c.isupper() else c for c in topic_part]).strip()
        else:
            topic = skill_id
    else:
        # 降級：若無課本例題，使用預設值
        textbook_example = ""  # Ab2/Ab3 會在 prompt 中顯示「無特定參考範例」
        topic = "數學題目"
    
    # 調用 PromptBuilder
    prompt = PromptBuilder.build(
        db_master_spec, 
        ablation_id=ablation_id, 
        textbook_example=textbook_example,
        topic=topic,
        skill_id=skill_id
    )
    
    # [實驗模式 4] 保存為 Golden Prompt
    if save_golden_prompt:
        # Ab2/Ab3 共用同一個 Ab2 文件
        prompt_ablation_id = 1 if ablation_id == 1 else 2
        golden_prompt_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'experiments', 'golden_prompts', 'temp'
        )
        
        # 確保目錄存在
        os.makedirs(golden_prompt_dir, exist_ok=True)
        
        golden_prompt_path = os.path.join(
            golden_prompt_dir,
            f'{skill_id}_Ab{prompt_ablation_id}.txt'
        )
        
        try:
            with open(golden_prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            if VERBOSE_LEVEL >= 1:
                print(f"   💾 已保存 Golden Prompt: {os.path.basename(golden_prompt_path)}")
        except Exception as e:
            if VERBOSE_LEVEL >= 1:
                print(f"   ⚠️ 無法保存 Golden Prompt: {e}")
    
    return prompt, topic, textbook_example

def _call_ai(prompt, model_config=None):
    """呼叫 AI 並回傳 raw_output, prompt_tokens, completion_tokens
    
    Args:
        prompt: 提示文本
        model_config: [NEW] 可选的模型配置字典，如果提供则使用，否则使用默认的 'coder' 角色
    """
    # [NEW FIX 2026-02-06] 如果提供了 model_config，使用它；否则使用默认的 'coder' 角色
    if model_config:
        # 使用提供的模型配置创建 AI 客户端
        provider = model_config.get('provider', 'local').lower()
        model_name = model_config.get('model', 'qwen2.5-coder:7b')
        temperature = model_config.get('temperature', 0.1)
        max_tokens = model_config.get('max_tokens', 2048)
        extra_body = model_config.get('extra_body', {})
        safety_settings = model_config.get('safety_settings') # [ADD] Ensure safety settings passed
        
        if provider in ['google', 'gemini']:
            from core.ai_wrapper import GoogleAIClient
            client = GoogleAIClient(
                model_name, 
                temperature, 
                max_tokens=max_tokens, 
                safety_settings=safety_settings
            )
        else:
            from core.ai_wrapper import LocalAIClient
            client = LocalAIClient(model_name, temperature, max_tokens=max_tokens, extra_body=extra_body)
    else:
        # 使用默认的 'coder' 角色客户端
        client = get_ai_client(role='coder')
    
    # [Refactored] 使用統一的 Retry 機制
    try:
        response = call_ai_with_retry(
            client=client, 
            prompt=prompt, 
            max_retries=3, 
            retry_delay=5, 
            verbose=(VERBOSE_LEVEL >= 1)
        )
    except Exception as e:
        # 重試失敗後，這裡捕獲最後的異常並回傳空值，避免程序崩潰
        if VERBOSE_LEVEL >= 1:
            print(f"   ❌ Final Failure in _call_ai: {e}")
        return "", 0, 0
    
    # 處理各種可能的 Response 格式
    raw_output = ""
    prompt_tokens = 0
    completion_tokens = 0
    
    if hasattr(response, 'text'):
        raw_output = response.text
    elif hasattr(response, 'content'): 
        raw_output = response.content
    else:
        raw_output = str(response)

    # [Qwen3 / DeepSeek] Extract thinking/reasoning content
    thinking_output = getattr(response, 'thinking', '') or ''

    try:
        if hasattr(response, 'usage_metadata'):
            prompt_tokens = response.usage_metadata.prompt_token_count
            completion_tokens = response.usage_metadata.candidates_token_count
        elif hasattr(response, 'usage'):
             prompt_tokens = response.usage.prompt_tokens
             completion_tokens = response.usage.completion_tokens
    except:
        pass
        
    return raw_output, prompt_tokens, completion_tokens, thinking_output

def _validate_code(final_code):
    """語法驗證"""
    return _validate_python_code(final_code)

def _dynamic_sampling(final_code):
    """
    動態採樣驗證 generate() 輸出 (Process-Isolated + Timeout 防止死迴圈)
    """
    import subprocess
    import sys
    import uuid
    import json
    
    dyn_ok = True
    sampling_success_count = 0
    sampling_total_count = 0
    error_msg = ''
    
    try:
        # 1. 準備臨時目錄與檔案
        root = path_in_root()
        temp_dir = ensure_dir(os.path.join(root, 'temp'))
        unique_id = uuid.uuid4().hex[:8]
        temp_filename = f"dyn_sample_{unique_id}.py"
        temp_path = os.path.join(temp_dir, temp_filename)
        wrapper_filename = f"wrapper_{unique_id}.py"
        wrapper_path = os.path.join(temp_dir, wrapper_filename)

        # 2. 寫入目標代碼
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(final_code)
            
        # 3. 寫入 Wrapper 腳本
        # 確保路徑轉義這用於生成的 Python 字串中
        root_escaped = root.replace('\\', '/')
        temp_path_escaped = temp_path.replace('\\', '/')
        
        wrapper_code = f"""import sys
import os
import json
import importlib.util

# Add project root needed for imports
sys.path.append('{root_escaped}')

try:
    # Load the module dynamically from file path
    spec = importlib.util.spec_from_file_location("temp_mod", r"{temp_path_escaped}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, 'generate'):
        print(json.dumps({{'status': 'error', 'msg': 'Function generate not found'}}))
        sys.exit(0)
        
    for i in range(3):
        res = module.generate()
        if not isinstance(res, dict) or 'question_text' not in res or 'answer' not in res:
             print(json.dumps({{'status': 'error', 'msg': 'Invalid return format'}}))
             sys.exit(0)
             
    print(json.dumps({{'status': 'ok'}}))
    
except Exception as e:
    print(json.dumps({{'status': 'error', 'msg': str(e)}}))
"""
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
            
        # 4. 執行子進程 (Timeout = 5秒)
        proc = subprocess.run(
            [sys.executable, wrapper_path],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=root
        )
        
        stdout_output = proc.stdout.strip()
        
        if proc.returncode != 0:
            dyn_ok = False
            error_msg = f"Runtime Error: {proc.stderr or stdout_output}"
        else:
            try:
                # 嘗試解析最後一行的 JSON
                lines = stdout_output.splitlines()
                last_line = lines[-1] if lines else "{}"
                res = json.loads(last_line)
                
                if res.get('status') == 'ok':
                    sampling_success_count = 3
                    sampling_total_count = 3
                else:
                    dyn_ok = False
                    error_msg = res.get('msg', 'Unknown Logic Error')
            except json.JSONDecodeError:
                dyn_ok = False
                error_msg = f"JSON Parse Failed. Output: {stdout_output}"
                
    except subprocess.TimeoutExpired:
        dyn_ok = False
        error_msg = "TIMEOUT: Code generation took > 5s (Infinite Loop Detected)"
        
    except Exception as e:
        dyn_ok = False
        error_msg = f"System Error: {str(e)}"
        
    finally:
        # 清理臨時檔案
        try:
            if os.path.exists(temp_path): os.remove(temp_path)
            if os.path.exists(wrapper_path): os.remove(wrapper_path)
        except:
            pass
            
    return dyn_ok, sampling_success_count, sampling_total_count, error_msg

def _format_header(skill_id, current_model, ablation_id, duration, prompt_tokens, completion_tokens, created_at, fix_status_str, fixes_str, verify_status_str):
    """產生檔案標頭"""
    header = f"""# ==============================================================================\n# ID: {skill_id}\n# Model: {current_model} | Strategy: V10.1 Modular Refactored\n# Ablation ID: {ablation_id} | Basic Cleanup: ENABLED | Advanced Healer: {'ON' if ablation_id>=2 else 'OFF'}\n# Performance: {duration:.2f}s | Tokens: In={prompt_tokens}, Out={completion_tokens}\n# Created At: {created_at}\n# Fix Status: {fix_status_str} | Fixes: {fixes_str}\n# Verification: Internal Logic Check = {verify_status_str}\n# ==============================================================================\n"""
    return header

def _write_file(out_path, header, final_code):
    ensure_dir(os.path.dirname(out_path))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(header + final_code)

def _log_experiment(**kwargs):
    """Log to DB"""
    try:
        log_entry = ExperimentLog(
            skill_id=kwargs.get('skill_id'),
            start_time=kwargs.get('start_time'),
            duration_seconds=time.time() - kwargs.get('start_time', time.time()),
            prompt_len=kwargs.get('prompt_len'),
            code_len=kwargs.get('code_len'),
            is_success=kwargs.get('is_valid'),
            error_msg=kwargs.get('error_msg'),
            repaired=kwargs.get('repaired'),
            model_name=kwargs.get('model_name'),
            prompt_tokens=kwargs.get('prompt_tokens'),
            completion_tokens=kwargs.get('completion_tokens'),
            total_tokens=kwargs.get('total_tokens'),
            ablation_id=kwargs.get('ablation_id'),
            raw_response=kwargs.get('raw_response'),
            final_code=kwargs.get('final_code')
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error logging experiment: {e}")
        try:
            db.session.rollback()
        except:
            pass

def regex_healer_v2(raw_code):
    """
    [Regex Fix: LaTeX 轉義保護]
    防止 \div 變成 \d (非法轉義)
    模式 A: 將單反斜線 LaTeX 符號轉為雙反斜線
    模式 B: 強制將包含 LaTeX 符號的字串轉換為原始字串 (Raw String)
    回傳: (processed_code, fix_count)
    """
    import re
    fix_count = 0
    processed_code = raw_code
    
    # 計算模式 A 需要替換的次數
    fix_count += processed_code.count('\\div') + processed_code.count('\\times')
    processed_code = processed_code.replace('\\div', '\\\\div').replace('\\times', '\\\\times')
    
    # 模式 B: 強制將包含 LaTeX 符號的字串轉換為原始字串 (Raw String)
    # 尋找 "..." 或 '...' 裡面含有 \div 或 \times 的，在其引號前補上 r
    processed_code, c = re.subn(r'(?<!r)(["\'])(.*?\\(?:div|times).*?\1)', r'r\1\2', processed_code)
    fix_count += c
    
    # [Regex Fix: 終極轉義修復]
    # 1. 偵測所有在 safe_eval 內的反斜線，將其物理替換為 python 可理解的符號
    # 這是因為 safe_eval 的輸入不需要 LaTeX 格式，只需要純運算邏輯
    def replace_safe_eval(m):
        inner = m.group(1).replace('\\\\div', '/').replace('\\div', '/').replace('\\\\times', '*').replace('\\times', '*')
        return f"IntegerOps.safe_eval('{inner}')"
        
    processed_code, c = re.subn(
        r'IntegerOps\.safe_eval\(f?"(.*?)"\)', 
        replace_safe_eval, 
        processed_code
    )
    fix_count += c
    
    # 2. 自動修正 question_text 中的單反斜線
    # 尋找非 raw string 且包含 \div 的字串，強制補上 r
    processed_code, c = re.subn(r'(?<!r)(["\'])(.*?\\div.*?\1)', r'r\1\2', processed_code)
    fix_count += c
    
    # 3. [Regex Fix: LaTeX 運算去汙]
    # 將所有在 safe_eval() 括號內的 LaTeX 符號轉為 Python 運算子
    # 這是最後一道防線，捕捉針對任何物件呼叫的 safe_eval
    def ultimate_replace_safe_eval(m):
        return m.group(0).replace('\\times', '*').replace('\\div', '/').replace('\\\\', '\\')
        
    processed_code, c = re.subn(
        r"safe_eval\((.*?)\)", 
        ultimate_replace_safe_eval, 
        processed_code
    )
    fix_count += c
    
    # 4. [Regex Fix: Unterminated string literal]
    # 修復 LLM 產生的多行字串 (如 f'計算 \n\n 的值。') 導致的 SyntaxError
    # 將跨行的單引號/雙引號字串自動轉換為三引號字串 (''' 或 """)
    processed_code, c1 = re.subn(r"(f?)(['])((?:[^'\\]|\\.)*?\n(?:[^'\\]|\\.)*?)[']", r"\1'''\3'''", processed_code)
    processed_code, c2 = re.subn(r'(f?)(["])((?:[^"\\]|\\.)*?\n(?:[^"\\]|\\.)*?)["]', r'\1"""\3"""', processed_code)
    fix_count += c1 + c2
    
    return processed_code, fix_count

def _basic_cleanup(code, strict_mode=True):
    """移除 markdown 標記與尾部說明文字（Qwen 違規檢測與移除）
    
    Args:
        code: 原始代碼
        strict_mode: 是否執行嚴格的尾部說明文字清理 (預設 True，Cloud 模型建議 False)
    """
    # 執行 LaTeX 保護
    code, regex_v2_fixes = regex_healer_v2(code)
    
    # 強行確保 question_text 裡的變數被正確包裝
    if "question_text = r" in code and "{{" not in code:
        # 這是為了防止 AI 忘記在 Raw string 裡處理變數嵌入
        code = code.replace(r"$$", f"$$\" + f\"{{...}}\" + r\"$$") # 這裡需要 Antigravity 根據 logic_spec 動態修正
        regex_v2_fixes += 1
    
    old_code = code
    
    # Step 1: 移除 markdown 標記 (總是執行)
    code = re.sub(r'^(\s*)```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^(\s*)```\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n(\s*)```\s*$', '', code, flags=re.MULTILINE)
    
    # Step 2: 移除尾部說明文字（僅 strict_mode 執行）
    # Step 2: 移除尾部說明文字（僅 strict_mode 執行）
    # [Unknown Fix 2026-02-15] Aggressive Cleanup for Chatty Models (Gemini/Qwen)
    # 強制移除代碼前後的對話內容，只保留核心代碼
    
    lines = code.split('\n')
    cleaned_lines = []
    found_code_start = False
    
    # 定義 Python 代碼的強特徵關鍵字 (Strong Signal)
    code_starters = ('import ', 'from ', 'def ', 'class ', '@', '#', 'if __name__')
    
    # 掃描並過濾
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 1. 尚未找到代碼開始：檢查是否為代碼行
        if not found_code_start:
            # 如果是空行，跳過
            if not stripped:
                continue
                
            # 如果是強特徵關鍵字，標記開始
            if stripped.startswith(code_starters):
                found_code_start = True
                cleaned_lines.append(line)
                continue
            
            # 如果是賦值語句 (且不是中文說明)，可能也是代碼
            # 但為了安全，我們傾向於相信 Strong Signal，或者包含 '=', 'return' 等
            if '=' in stripped and not re.search(r'[\u4e00-\u9fff]', stripped):
                 found_code_start = True
                 cleaned_lines.append(line)
                 continue
            
            # 其他情況：視為 Intro Text (對話)，丟棄！
            # (例如: "Here is the code...", "以下是...")
            continue
            
        else:
            # 2. 已經在代碼區塊內：檢查是否為結尾說明 (Outro)
            # 如果遇到明顯的 Markdown 標題 (###) 或長段中文說明，且不是註解，則截斷
            
            # Exclude: Generate 結尾的文字
            if stripped.startswith('###') or stripped.startswith('Note:') or stripped.startswith('Explanation:'):
                break
                
            # 如果是純中文說明且沒有 #，視為結束
            if re.match(r'^[\u4e00-\u9fff]', stripped) and not stripped.startswith('#'):
                 # 雙重確認：有些字串可能包含中文
                 # 如果行內有 quote ('或")，可能是合法的 python string
                 if not ("'" in stripped or '"' in stripped):
                     break
            
            cleaned_lines.append(line)
    
    # 重組代碼
    code = '\n'.join(cleaned_lines).strip()
    
    cleanup_fixes = 1 if code != old_code else 0
    total_fixes = regex_v2_fixes + cleanup_fixes
    
    return code, total_fixes


def _advanced_healer(clean_code, ablation_id, skill_id, ai_client=None):
    """進階 Healer：委派給 RegexHealer 與 ASTHealer"""
    
    # Step 2: Regex 修復 (Ab2/Ab3)
    if ablation_id == 2:
        log_step_start(2, "Minimal Healer (Ab2 Only)", "[基礎設施支援] Import Injection Only...")
    else:
        log_step_start(2, "Regex Healer (Ab3)", "[進階修復啟動] Regex Pattern Matching...")
    
    regex_healer = RegexHealer()
    code_before_regex = clean_code
    
    # [V3.0 Ablation Fix] Ab2 使用最小化修復，Ab3 使用完整修復
    if ablation_id == 2:
        code_after_regex, regex_stats = regex_healer.heal_minimal(clean_code)
    else:  # Ab3 or higher
        code_after_regex, regex_stats = regex_healer.heal(clean_code)
    
    # [FIX 2026-02-07] RegexHealer.heal() 現在返回 stats dict，需要提取 regex_fix_count
    regex_fixes = regex_stats.get('regex_fix_count', 0) if isinstance(regex_stats, dict) else regex_stats
    
    if VERBOSE_LEVEL == 2:
        log_fix_detail("", "skip", "")  # 空行
        
        if ablation_id == 2:
            # Ab2 Minimal Healing Log
            log_fix_detail("2.1 Import Injection", "fixed" if regex_stats.get('imports_injected', 0) > 0 else "skip",
                          f"🔍 自動注入 {regex_stats.get('imports_injected', 0)} 個 import")
        else:
            # Ab3 Full Healing Log
            log_fix_detail("2.0  Complexity Checker", "warn", "⚠️  未使用分數 (建議檢查 MASTER_SPEC)")
            log_fix_detail("2.05 Loop Breaker", "fixed" if "while True" in code_before_regex else "skip",
                          "🔍 掃描危險迴圈: while True, while 1, while (True)")
            log_fix_detail("2.1  Garbage Cleaner", "skip", "🔍 掃描孤立字符: `, ```...")
            log_fix_detail("2.2  Hallucination Killer", "skip", "🔍 掃描幻覺函數: clean_expression")
            log_fix_detail("2.5  LaTeX Protector", "fixed" if regex_fixes > 0 else "skip",
                          "🔍 檢查 Domain Helper 輸出")
            log_fix_detail("2.3  Tuple Return Fixer", "skip", "🔍 檢查返回格式")
            log_fix_detail("2.35 Answer Format Fixer", "fixed" if regex_fixes > 1 else "skip",
                          "🔍 檢查答案格式")

    # [Healer Check: 硬編碼獵殺]
    if "question_text = r" in code_after_regex and "fmt(" not in code_after_regex and "{" not in code_after_regex:
        raise ValueError("Healer: Detected Hard-coded string! You must use f-string with variables.")
        
    # 檢查是否有直接賦值數字 (例如 v1 = 8)
    if re.search(r'\b[a-zA-Z_]\w*\s*=\s*-?\d+\s*(\n|#)', code_after_regex):
        if "level=" not in code_after_regex and "max_retries" not in code_after_regex and "FourOperationsOfRadicals" not in str(skill_id or ""):
            raise ValueError("Healer: Detected HARD-CODED numbers! You MUST use IntegerOps.random_nonzero().")

    # [NEW FIX: Healer 強制注入 Check Function]
    if ablation_id >= 3:
        if "def check" not in code_after_regex:
            code_after_regex += "\n\ndef check(user_answer, correct_answer):\n    try:\n        return {'correct': str(user_answer).strip() == str(correct_answer).strip(), 'result': '自動補全比對'}\n    except:\n        return {'correct': False, 'result': '錯誤'}"
            regex_fixes += 1
            if VERBOSE_LEVEL == 2:
                log_fix_detail("2.6 Check Function Injector", "fixed", "✅ 成功補全缺漏的 check 函式")
    
    log_step_result(2, regex_fixes, f"代碼長度: {len(code_before_regex)} → {len(code_after_regex)} 字符")
    
    # Step 3: AST 修復 (僅 Ab3)
    if ablation_id >= 3:
        log_step_start(3, "AST Healer (Ab3 Only)", "[語法樹修復啟動] Abstract Syntax Tree Analysis...")
        
        # [V50.0] 傳入 AI Client 以支援 Semantic Healing
        if ai_client is None:
             ai_client = get_ai_client() # Fallback to default
             
        ast_healer = ASTHealer(ai_client=ai_client)
        try:
            # 3.1 靜態 AST 修復
            code_after_ast, ast_fixes = ast_healer.heal(code_after_regex)
            
            if VERBOSE_LEVEL == 2:
                log_fix_detail("", "skip", "")
                log_fix_detail("3.1 Parse AST", "fixed", "✅ 語法樹解析成功")
                log_fix_detail("3.2 Hallucination Function Fixer", "skip", "🔍 檢查未定義函數")
                log_fix_detail("3.3 Dangerous Call Remover", "skip", "🔍 檢查危險函數: eval, exec, safe_eval")
                log_fix_detail("3.4 Loop Condition Fixer", "skip", "🔍 檢查迴圈條件")
            
            # [V50.0] Semantic Self-Correction (邏輯修復)
            # 先進行一次快速驗證，如果有 SyntaxError 或 NameError 等嚴重錯誤，才啟動 LLM 修復
            try:
                # 簡單的 compile 檢查 (不執行，只查語法與變數綁定)
                compile(code_after_ast, '<string>', 'exec')
                
                # [V50.1] Simulation & Rescue (模擬執行與救援)
                # 進一步捕捉 runtime 錯誤 (如 NameError: name 'val_A' is not defined)
                # 因為代碼片段可能依賴 utils，我們只在它看起來完整時嘗試
                
                # 使用 validator 進行沙盒模擬
                # 注意：這會比較慢，但能抓到邏輯漏洞
                is_valid_sim, sim_error = _validate_python_code(code_after_ast)
                
                if not is_valid_sim:
                    if VERBOSE_LEVEL == 2:
                        # 簡化錯誤訊息顯示
                        preview_err = sim_error.split('\n')[-1] if sim_error else "Unknown Error"
                        log_fix_detail("3.6 Simulation Check", "warn", f"⚠️  模擬執行失敗: {preview_err}")
                        log_fix_detail("3.7 Semantic Rescue", "active", "🚑 啟動 Rescue Mission...")
                    
                    # 啟動救援
                    fixed_code, is_fixed = ast_healer.semantic_heal(code_after_ast, sim_error)
                    
                    if is_fixed:
                        code_after_ast = fixed_code
                        # 更新計數 (ast_healer.fixes 已在內部增加)
                        ast_fixes = ast_healer.fixes
                        if VERBOSE_LEVEL == 2:
                            log_fix_detail("3.7 Semantic Rescue", "fixed", "✅ 成功修復 Runtime Error")
            
            except Exception as e:
                # 如果 compile 就失敗，直接啟動 Semantic Heal
                if VERBOSE_LEVEL == 2:
                    log_fix_detail("3.5 Semantic Self-Correction", "warn", f"⚠️  Syntax 嚴重錯誤，啟動 LLM 修復: {e}")
                
                fixed_code, is_fixed = ast_healer.semantic_heal(code_after_ast, str(e))
                if is_fixed:
                    code_after_ast = fixed_code
                    pass

            # 更新總修復數
            ast_fixes = ast_healer.fixes
            
            log_step_result(3, ast_fixes, f"AST 結構正常" if ast_fixes == 0 else f"修復完成")
            
            # [V51 ADD] Append logs to a dynamic object returned
            class ASTStats:
                pass
            ast_stats = ASTStats()
            ast_stats.logs = ast_healer.logs
            
        except Exception as e:
            if VERBOSE_LEVEL >= 1:
                print(f"│ ❌ AST 解析失敗: {e}")
            
            # [NEW] Fail-fast for Ablation 3
            if ablation_id == 3:
                # AST 徹底失敗時，嘗試最後一次 Semantic Heal
                # (因為 parse 失敗代表連 AST 都建不起來)
                try: 
                    if VERBOSE_LEVEL == 2:
                        log_fix_detail("Emergency Semantic Heal", "warn", "⚠️ AST Parse Failed - Trying LLM Fix")
                    
                    fixed_code, is_fixed = ast_healer.semantic_heal(code_after_regex, f"SyntaxError: {str(e)}")
                    if is_fixed:
                        code_after_ast = fixed_code
                        ast_fixes = ast_healer.fixes
                    else:
                        code_after_ast = code_after_regex
                        ast_fixes = 0
                except:
                    if VERBOSE_LEVEL == 2:
                        log_fix_detail("Fail-fast Protection", "warn", 
                                      "⚠️ AST 解析失敗，使用 Regex 修復後的代碼")
                        log_fix_detail("Safety Net", "warn", 
                                      "如有無窮迴圈，將在動態採樣階段被 timeout 攔截")
                    code_after_ast = code_after_regex
                    ast_fixes = 0

                log_step_result(3, ast_fixes, "使用 Regex 修復後的代碼（AST 失敗）")
                class ASTStats:
                    pass
                ast_stats = ASTStats()
                ast_stats.logs = ast_healer.logs
            else:
                code_after_ast = code_after_regex
                ast_fixes = 0
                class ASTStats:
                    pass
                ast_stats = ASTStats()
                ast_stats.logs = []
    else:
        code_after_ast = code_after_regex
        ast_fixes = 0
        class ASTStats:
            pass
        ast_stats = ASTStats()
        ast_stats.logs = []
        
    # [NEW] Code Regex Diff Logging for Live Show UI
    if code_before_regex != code_after_regex:
        import difflib
        _diff = difflib.unified_diff(
            code_before_regex.splitlines(),
            code_after_regex.splitlines(),
            n=0, lineterm=''
        )
        ast_stats.logs.append("[CODE_REGEX_DIFF] Regex 程式碼內容修復：")
        for _dl in _diff:
            if _dl.startswith("+++") or _dl.startswith("---") or _dl.startswith("@@"):
                continue
            if _dl.startswith("-"):
                ast_stats.logs.append(f"[CODE_REGEX_DIFF] ❌ 移除: {_dl[1:].strip()}")
            elif _dl.startswith("+"):
                ast_stats.logs.append(f"[CODE_REGEX_DIFF] ✅ 修改/新增: {_dl[1:].strip()}")
    
    # [NEW 2026-02-08] Step 4.5 + 7.5: Anti-Duplication & Variable-Before-Use Checker (僅 Ab3)
    anti_dup_fixes = 0
    var_check_fixes = 0
    code_after_anti_dup = code_after_ast
    
    if ablation_id >= 3:
        log_step_start(4.5, "Anti-Duplication & Variable Checker (Ab3 Only)", 
                      "[自癒機制] 檢測重複定義和變量問題...")
        
        try:
            code_after_anti_dup, anti_dup_fixes = heal_unified(code_after_ast)
            
            if VERBOSE_LEVEL == 2:
                log_fix_detail("4.5 Anti-Duplication", "fixed" if anti_dup_fixes > 0 else "skip",
                              f"✅ 清理 {anti_dup_fixes} 個重複定義或變量問題" if anti_dup_fixes > 0 else "無需修復")
            
            log_step_result(4.5, anti_dup_fixes, f"修復完成" if anti_dup_fixes > 0 else "無需修復")
        except Exception as e:
            if VERBOSE_LEVEL >= 1:
                print(f"│ ⚠️ Anti-Duplication 修復失敗: {e}")
            code_after_anti_dup = code_after_ast
            anti_dup_fixes = 0
            log_step_result(4.5, 0, "跳過（修復失敗，使用 AST 修復後的代碼）")
    
    # 這裡可擴充更多修復統計資訊
    if ablation_id >= 3:
        pass
    
    total_fixes = regex_fixes + ast_fixes + anti_dup_fixes + var_check_fixes
    
    garbage_cleaner_count = 0
    removed_list = []
    healer_fixes = regex_fixes + ast_fixes + anti_dup_fixes
    eval_eliminator_count = 0
    healing_duration = 0
    
    # Return code_after_anti_dup, regex_fixes, ast_fixes, [ast_stats as last element]
    return code_after_anti_dup, regex_fixes, ast_fixes, ast_stats, garbage_cleaner_count, removed_list, healer_fixes, eval_eliminator_count, healing_duration


def _post_ast_fixes(clean_code, skill_id):
    """F.12/F.13/F.14 Post-AST Fixes (暫時直接回傳，若有特殊後處理可委派到 healers)"""
    # 若有特殊後處理需求，可在 healers/ast_healer.py 中擴充
    qwen_fixes = 0
    return clean_code, qwen_fixes

def auto_generate_skill_code(skill_id, queue=None, **kwargs):
    start_time = time.time()
    
    # [NEW FIX 2026-02-06] 根據 model_size_class 參數選擇正確的模型配置
    # 映射: 'cloud' -> Gemini, '14b' -> Qwen 14B, '7b' -> Qwen 7B
    model_size_class = kwargs.get('model_size_class', '14b')
    
    # 构建 model_key 映射
    model_size_to_preset = {
        'cloud': 'gemini-3-flash',
        '14b': 'qwen3-14b', # [UPDATED 2026-02-13] Point to Qwen3 preset
        '7b': Config.DEFAULT_CODER_PRESET
    }
    
    model_preset_key = model_size_to_preset.get(model_size_class, 'qwen2.5-coder-14b')
    
    # 从 CODER_PRESETS 获取模型配置，如果不存在则降级到 MODEL_ROLES
    if model_preset_key in Config.CODER_PRESETS:
        role_config = Config.CODER_PRESETS[model_preset_key]
    else:
        role_config = Config.MODEL_ROLES.get('coder', {'provider': 'google', 'model': 'gemini-1.5-flash'})
    
    current_model = role_config.get('model', 'Unknown')
    ablation_id = kwargs.get('ablation_id', 3)
    use_golden_prompt = kwargs.get('use_golden_prompt', False)  # [NEW] 實驗模式 2 參數
    save_golden_prompt = kwargs.get('save_golden_prompt', False)  # [NEW] 實驗模式 4 參數
    
    # Ablation Settings
    # [2026-02-01 Bug Fix] 嚴格遵守實驗設計的變因分離：
    # - Ab1: 無 Healer（僅基礎清理）- 測試模型原生智商
    # - Ab2: 無 Healer（僅基礎清理）- 測試 Prompt 工程 + 工具注入
    # - Ab3: 有 Healer (Regex + AST) - 測試自癒機制
    ablation_config = AblationSetting.query.get(ablation_id)
    if ablation_config:
        use_regex_healer = ablation_config.use_regex
        use_ast_healer = ablation_config.use_ast
        ablation_name = ablation_config.name
    else:
        # Fallback: 確保變因分離
        use_regex_healer = (ablation_id >= 3)  # 只有 Ab3 啟用 Regex Healer
        use_ast_healer = (ablation_id >= 3)    # 只有 Ab3 啟用 AST Healer
        ablation_name = f"Ablation-{ablation_id}"

    custom_output_path = kwargs.get('custom_output_path', None)
    
    # 打印 Pipeline 启动标题
    log_pipeline_header(skill_id, ablation_id, ablation_name)
    
    # Get DB Spec (作為 Fallback)
    active_prompt = SkillGenCodePrompt.query.filter_by(skill_id=skill_id, prompt_type="MASTER_SPEC").order_by(SkillGenCodePrompt.created_at.desc()).first()
    db_master_spec = active_prompt.prompt_content if active_prompt else "生成一題簡單的整數四則運算。"
    
    # Prompt 構建（可能讀取 Golden Prompt 或保存新的 Golden Prompt）
    prompt, topic, textbook_example = _build_prompt(
        skill_id, ablation_id, db_master_spec, 
        use_golden_prompt=use_golden_prompt,
        save_golden_prompt=save_golden_prompt
    )
    
    # Step 0: AI 生成
    log_step_start(0, "AI Code Generation", f"Model: {current_model}")
    if VERBOSE_LEVEL == 2:
        log_fix_detail("Prompt Length", "skip", f"{len(prompt)} tokens")
    
    # [FIX 2026-02-06] 传递 role_config 以确保使用正确的模型
    raw_output, prompt_tokens, completion_tokens = _call_ai(prompt, model_config=role_config)
    
    # [DEBUG 2026-02-13] Inspect Raw Output
    if VERBOSE_LEVEL >= 1:
        print(f"\n[DEBUG] Raw Output Preview (First 500 chars):\n{raw_output[:500]!r}\n")
    
    ai_gen_time = time.time() - start_time
    if VERBOSE_LEVEL == 2:
        log_fix_detail("Response Tokens", "skip", f"{completion_tokens} tokens")
        log_fix_detail("Generation Time", "skip", f"{ai_gen_time:.2f}s")
    log_step_result(0, 0, f"AI 生成完成 ({ai_gen_time:.2f}s, {completion_tokens} tokens)")
    
    # Step 1: 基礎清理 (All Ablations)
    log_step_start(1, "Basic Cleanup (All Ablations)", "[進階修復啟動] Markdown + Trimming...")
    if VERBOSE_LEVEL == 2:
        code_len_before = len(raw_output)
    
    # Cloud 模型通常生成質量較高，不需要激進的去說明文字清理（避免誤刪 docstring）
    is_cloud_model = (model_size_class == 'cloud')
    # [FIX] 恢復 strict_mode 邏輯：Local 模型通常較多話，需要嚴格清理；Cloud 模型則較為精簡
    strict_cleanup = not is_cloud_model
    clean_code, basic_cleanup_fixes = _basic_cleanup(raw_output, strict_mode=strict_cleanup)
    
    if VERBOSE_LEVEL == 2:
        code_len_after = len(clean_code)
        log_fix_detail("[1/4] 檢查 ```python 標記", "fixed" if markdown_cleanup_count > 0 else "skip", 
                      f"{'→ ✓ 發現 1 處' if markdown_cleanup_count > 0 else '→ ○ 無需修復'}")
        log_fix_detail("[2/4] 檢查 ``` 標記", "skip", "→ ○ 無需修復")
        log_fix_detail("[3/4] 檢查結尾標記", "skip", "→ ○ 無需修復") 
        log_fix_detail("[4/4] 清理前後空白", "fixed", "→ ✓ 完成")
    
    log_step_result(1, basic_cleanup_fixes, f"代碼長度: {len(raw_output)} → {len(clean_code)} 字符")
    
    regex_fixes = 0
    ast_fixes = 0
    garbage_cleaner_count = 0
    removed_list = []
    healer_fixes = 0
    eval_eliminator_count = 0
    healing_duration = 0
    
    # Step 2/3: 進階 Healer
    if use_regex_healer:
        clean_code, regex_fixes, ast_fixes, garbage_cleaner_count, removed_list, healer_fixes, eval_eliminator_count, healing_duration = _advanced_healer(clean_code, ablation_id, skill_id)
        # [DEBUG] Track fixer values
        if VERBOSE_LEVEL >= 2:
            print(f"[DEBUG] After _advanced_healer: regex_fixes={regex_fixes}, ast_fixes={ast_fixes}, healer_fixes={healer_fixes}")
        
    # F.12/F.13/F.14 Post-AST Fixes
    clean_code, qwen_fixes = _post_ast_fixes(clean_code, skill_id)
    
    # 組裝 final_code
    # [2026-02-01 Bug Fix] 嚴格遵守實驗設計：
    # - Ab1 (Bare): 無工具庫，純 AI 生成
    # - Ab2/Ab3: 有工具庫 (PERFECT_UTILS + Domain Functions)
    if ablation_id >= 2:
        # Ab2, Ab3: 注入完整工具庫
        skeleton = build_calculation_skeleton(skill_id)
        final_code = skeleton + "\n" + clean_code
    else:
        # Ab1 (Bare): 不注入工具庫，測試模型原生能力
        # 只包含 AI 生成的代碼（靠 random/math 等標準庫）
        final_code = clean_code
        
    # Step 4: 驗證
    # [NEW STEP: Domain Library Injection] 2026-02-16
    # 自動注入 Domain Libraries (如 RadicalOps) 的完整實作，使檔案 Self-Contained
    final_code, injected_libs = _inject_domain_libs(final_code)
    if injected_libs:
        injected_count = len(injected_libs)
        # Update logging strings if needed, though they are constructed later
        if VERBOSE_LEVEL >= 1:
            print(f"   💉 [Domain Injector] Injected {injected_count} libraries: {', '.join(injected_libs)}")

    # Step N: Validation
    is_valid, error_msg = _validate_code(final_code)
    
    # Step 5: 動態採樣
    log_step_start(5, "Dynamic Sampling (Safety Net)", "[執行驗證] Subprocess with 5s Timeout...")
    
    if is_valid:
        dyn_ok, sampling_success_count, sampling_total_count, dyn_error_msg = _dynamic_sampling(final_code)
        
        if VERBOSE_LEVEL == 2:
            log_fix_detail("", "skip", "")
            for i in range(sampling_total_count):
                status = "fixed" if i < sampling_success_count else "skip"
                log_fix_detail(f"Sample {i+1}/{sampling_total_count}:", status, 
                              f"✓ 生成成功" if i < sampling_success_count else "✗ 生成失敗")
        
        log_step_result(5, 0, f"驗證: {sampling_success_count}/{sampling_total_count} 通過 | Timeout: 5s")
    else:
        dyn_ok = False
        sampling_success_count = 0
        sampling_total_count = 0
        dyn_error_msg = error_msg
        if VERBOSE_LEVEL >= 1:
            print(f"│ ❌ 代碼驗證失敗: {error_msg}")
        log_step_result(5, 0, f"跳過（代碼無效）")
    
    duration = time.time() - start_time
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fix_status_str = "[Advanced Healer]" if (regex_fixes > 0 or ast_fixes > 0) else ("[Basic Cleanup]" if basic_cleanup_fixes > 0 else "[Clean Pass]")
    verify_status_str = "PASSED" if (is_valid and dyn_ok) else "FAILED"
    fixes_str = f"Basic={basic_cleanup_fixes}, Advanced=(Regex={regex_fixes}, AST={ast_fixes})"
    
    # [DEBUG] Track final Fix Status
    if VERBOSE_LEVEL >= 1:
        print(f"[DEBUG] Final Fix Status: {fix_status_str} | {fixes_str}")
    
    # 打印最终总结
    total_fixes_display = f"Basic={basic_cleanup_fixes}, Regex={regex_fixes}, AST={ast_fixes}"
    log_pipeline_summary(total_fixes_display, verify_status_str, duration)
    
    header = _format_header(skill_id, current_model, ablation_id, duration, prompt_tokens, completion_tokens, created_at, fix_status_str, fixes_str, verify_status_str)
    
    # 檔案寫入
    model_size_class = kwargs.get('model_size_class', '14b')
    if custom_output_path:
        out_path = custom_output_path
    else:
        skills_dir = ensure_dir(path_in_root('skills'))
        # [Fix] 直接生成帶 Ablation 標記的檔名（統一小寫）
        # 格式: gh_ApplicationsOfDerivatives_14b_Ab1.py
        file_name = f"{skill_id}_{model_size_class.lower()}_Ab{ablation_id}.py"
        out_path = os.path.join(skills_dir, file_name)
        
    try:
        _write_file(out_path, header, final_code)
        print(f"✅ [{skill_id}] File written: {os.path.abspath(out_path)}")
    except Exception as e:
        print(f"❌ [{skill_id}] Failed to write file: {e}")
        
    # Log
    _log_experiment(
        skill_id=skill_id,
        start_time=start_time,
        prompt_len=len(prompt),
        code_len=len(final_code),
        is_valid=is_valid and dyn_ok,
        error_msg=error_msg or dyn_error_msg,
        repaired=(regex_fixes > 0 or ast_fixes > 0),
        model_name=current_model,
        final_code=final_code,
        raw_response=raw_output,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        ablation_id=ablation_id
    )
    
    return is_valid and dyn_ok, "V10.1 Generated", {
        'tokens': prompt_tokens + completion_tokens,
        'score_syntax': 100.0 if (is_valid and dyn_ok) else 0.0,
        'total_fixes': regex_fixes + ast_fixes,
        'regex_fixes': regex_fixes,
        'ast_fixes': ast_fixes,
        'is_valid': is_valid and dyn_ok
    }

# ==============================================================================
# 3. 完美工具庫 (Perfect Utils - Dynamic Builder)
# ==============================================================================

def _build_perfect_utils():
    """
    [V10.1] 動態從新模組中提取工具函數源代碼（簡化版）
    直接讀取檔案並移除模組頭註解，保持代碼完整性
    """
    from pathlib import Path
    
    # 1. 基礎 imports
    base_imports = '''import random
from random import randint, choice
import math
from fractions import Fraction
import re
import ast
import operator
import os

# ✅ 預設的 LaTeX 運算子映射（四則）- 全域可用
op_latex = {'+': '+', '-': '-', '*': '\\\\times', '/': '\\\\div'}

'''
    
    # 2. 動態讀取 code_utils 模組的源代碼
    try:
        # 假設 code_utils 位於 core/code_utils
        current_dir = Path(__file__).parent
        code_utils_dir = current_dir / 'code_utils'
        
        # 簡易檢查：如果當前檔案在 core 下，則 code_utils 就在旁邊
        # 如果路徑錯誤，嘗試調整
        if not code_utils_dir.exists():
            # 嘗試專案根目錄下的 core/code_utils
             pass 

        all_code = []
        
        # 讀取各個工具模組
        for module_file in ['math_utils.py', 'latex_utils.py', 'file_utils.py']:
            file_path = code_utils_dir / module_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 找到第一個函數定義的位置，跳過模組頭
                code_start = 0
                in_docstring = False
                for i, line in enumerate(lines):
                    # 跳過模組級的 docstring
                    if '"""' in line or "'''" in line:
                         if line.count('"""') == 2 or line.count("'''") == 2:
                             continue # 單行docstring
                         in_docstring = not in_docstring
                         continue
                    if in_docstring:
                        continue
                    # 跳過 import 語句和空行
                    if line.strip().startswith('import ') or \
                       line.strip().startswith('from ') or \
                       line.strip() == '' or \
                       line.strip().startswith('#'):
                        continue
                    # 找到第一個函數或類定義
                    if line.strip().startswith('def ') or line.strip().startswith('class '):
                        code_start = i
                        break
                
                # 提取從第一個定義開始的所有代碼
                if code_start > 0:
                    function_code = ''.join(lines[code_start:])
                    all_code.append(function_code)
        
        # 3. 組合完整的 PERFECT_UTILS
        return base_imports + '\n'.join(all_code)
        
    except Exception as e:
        # 降級：如果無法讀取，返回最小集合
        print(f"⚠️  無法動態構建 PERFECT_UTILS: {e}，使用最小集合")
        return base_imports + '''
# [REFACTORED] 已搬移到 code_utils.math_utils
# - safe_choice, to_latex, fmt_num 已在 code_utils 中定義並導入
# 這些函數的完整版本已通過 import 導入，此處不再重複定義
'''

PERFECT_UTILS = _build_perfect_utils()

# ==============================================================================
# 3. 骨架與 Prompt 定義
# ==============================================================================
def build_calculation_skeleton(skill_id=None):
    """
    動態構建代碼框架，根據 skill_id 自動注入對應的 Domain 函數庫
    
    參數:
        skill_id: str, 例如 'gh_ApplicationsOfDerivatives'
    
    返回:
        str: 包含 PERFECT_UTILS + Domain Functions 的完整代碼框架
    """
    skeleton = r'''

# [INJECTED UTILS]
''' + PERFECT_UTILS + r'''
'''
    
    # [V47.14 新增] 動態注入 Domain 函數庫
    if skill_id:
        from core.prompts.domain_function_library import get_required_domains, get_domain_helpers_code
        
        required_domains = get_required_domains(skill_id)
        if required_domains:
            domain_code = get_domain_helpers_code(required_domains)
            skeleton += f'\n# [DOMAIN HELPERS - Auto-Injected for {skill_id}]\n'
            skeleton += domain_code + '\n'
    
    skeleton += r'''

# [AI GENERATED CODE]
# ---------------------------------------------------------
''' + "\n"
    
    return skeleton

# 保留舊的 CALCULATION_SKELETON 常量（向後兼容）
CALCULATION_SKELETON = build_calculation_skeleton()
